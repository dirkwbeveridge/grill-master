#!/usr/bin/env python3
"""Validate the known simulator artifact and export only its public screenshot evidence.

No network, git, Apple credentials, build archives, or logs are read by this helper.
Run with --self-test for offline positive/negative fixture coverage.
"""
from __future__ import annotations

import argparse
import binascii
import json
import os
from pathlib import Path
import shutil
import stat
import struct
import tempfile
import unittest
from unittest.mock import patch
import io
import zlib

SOURCE_RUN = 41384119053
SOURCE_SHA = "cb52b374bd21963bf390f5917cfa2cb2520bb0cc"
SOURCE_REPO = "dirkwbeveridge/grill-master"
CAPTURES = {
    f"{family}-{state}.png": (family, f"grillmaster://{state}")
    for family in ("iphone", "ipad")
    for state in ("configure", "temperatures")
}
ALLOWLIST = frozenset((*CAPTURES, "capture-manifest.json"))
LIMITATIONS = [
    "Simulator captures; physical device validation remains required.",
    "Active-cook screenshots require real UI automation and are not fabricated.",
]
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_PNG_BYTES = 25 * 1024 * 1024
MAX_MANIFEST_BYTES = 32 * 1024


class InvalidCapture(ValueError):
    """The artifact cannot be safely exported as the expected evidence."""


def require(condition, message):
    if not condition:
        raise InvalidCapture(message)


def annotation(level, message):
    """Escape workflow-command text; callers supply fixed reasons, never file contents."""
    escaped = message.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
    print(f"::{level} title=Native capture export::{escaped}", flush=True)


def failure_reason(exc):
    if isinstance(exc, InvalidCapture):
        return str(exc)
    # OSError text may contain paths or arbitrary arguments; report only its numeric code.
    return f"Filesystem operation failed (errno {exc.errno})"


def reject_symlink_ancestors(path):
    """Check without resolving first, which would hide a symlink."""
    for candidate in (path, *path.parents):
        require(not candidate.is_symlink(), "Source/output paths must not contain symlinks")


def read_regular(path, limit):
    # O_NOFOLLOW also closes the final-component symlink race after directory validation.
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
        with os.fdopen(descriptor, "rb") as stream:
            require(stat.S_ISREG(os.fstat(stream.fileno()).st_mode), "Expected regular files only")
            content = stream.read(limit + 1)
    except OSError as exc:
        raise InvalidCapture("Unable to read a regular artifact file") from exc
    require(len(content) <= limit, "Artifact file exceeds its size limit")
    return content


def png_dimensions(content):
    """Read dimensions and validate PNG framing/CRCs without image dependencies."""
    require(content.startswith(PNG_MAGIC), "Invalid PNG signature")
    offset = len(PNG_MAGIC)
    dimensions = None
    seen_data = False
    seen_end = False
    while offset < len(content):
        require(offset + 12 <= len(content), "Truncated PNG chunk")
        size = struct.unpack_from(">I", content, offset)[0]
        kind = content[offset + 4:offset + 8]
        end = offset + 12 + size
        require(end <= len(content), "Truncated PNG chunk payload")
        require(len(kind) == 4 and all(65 <= c <= 90 or 97 <= c <= 122 for c in kind),
                "Invalid PNG chunk name")
        payload = content[offset + 8:offset + 8 + size]
        crc = struct.unpack_from(">I", content, offset + 8 + size)[0]
        require(binascii.crc32(kind + payload) & 0xFFFFFFFF == crc, "Invalid PNG checksum")
        if dimensions is None:
            require(kind == b"IHDR" and size == 13, "PNG is missing its dimensions header")
            width, height, depth, color, compression, filtering, interlace = struct.unpack(">IIBBBBB", payload)
            require(0 < width <= 8192 and 0 < height <= 8192 and width * height <= 32_000_000,
                    "PNG dimensions are missing or outside capture limits")
            depths = {0: (1, 2, 4, 8, 16), 2: (8, 16), 3: (1, 2, 4, 8),
                      4: (8, 16), 6: (8, 16)}
            require(depth in depths.get(color, ()) and compression == 0 and filtering == 0
                    and interlace in (0, 1), "Invalid PNG image header")
            dimensions = (width, height)
        elif kind == b"IHDR":
            raise InvalidCapture("Duplicate PNG dimensions header")
        elif kind == b"IDAT":
            seen_data = True
        elif kind == b"IEND":
            require(size == 0 and seen_data, "PNG is missing image data")
            require(end == len(content), "Unexpected bytes after PNG end")
            seen_end = True
        elif kind[0] < 97:
            require(kind == b"PLTE", "Unsupported critical PNG chunk")
        offset = end
    require(dimensions is not None and seen_end, "PNG is incomplete")
    return dimensions


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "Duplicate JSON keys are not permitted")
        result[key] = value
    return result


def validate_manifest(content):
    try:
        manifest = json.loads(content.decode("utf-8"), object_pairs_hook=unique_object)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise InvalidCapture("Capture manifest must be valid UTF-8 JSON") from exc
    require(isinstance(manifest, dict) and set(manifest) == {"runtime", "captures", "limitations"},
            "Unexpected manifest fields")
    runtime = manifest["runtime"]
    require(isinstance(runtime, str) and runtime.startswith("iOS ") and len(runtime) <= 40,
            "Missing iOS runtime")
    version = runtime[4:].split(".")
    require(2 <= len(version) <= 3 and all(p.isascii() and p.isdigit() for p in version),
            "Invalid iOS runtime version")
    require(manifest["limitations"] == LIMITATIONS, "Unexpected capture limitations")
    captures = manifest["captures"]
    require(isinstance(captures, list) and len(captures) == len(CAPTURES), "Expected four captures")
    names = set()
    for item in captures:
        require(isinstance(item, dict) and set(item) == {"file", "device", "route"},
                "Unexpected capture fields")
        name = item["file"]
        require(isinstance(name, str) and name in CAPTURES and name not in names,
                "Unexpected or duplicate capture filename")
        family, route = CAPTURES[name]
        device = item["device"]
        prefix = "iPhone " if family == "iphone" else "iPad "
        require(isinstance(device, str) and device.startswith(prefix) and len(device) <= 120
                and device.isprintable(), "Missing or mismatched simulator device")
        require(item["route"] == route, "Capture route does not match its filename")
        names.add(name)
    require(names == set(CAPTURES), "Capture manifest is incomplete")
    return manifest


def validate_source(source):
    source = Path(os.path.abspath(source))
    reject_symlink_ancestors(source)
    require(source.is_dir(), "Artifact source must be a directory")
    entries = list(source.iterdir())
    require({entry.name for entry in entries} == ALLOWLIST, "Artifact files do not match the allowlist")
    require(all(not entry.is_symlink() and entry.is_file() for entry in entries),
            "Artifact must contain regular files only, without directories or symlinks")
    # Snapshot each validated file in memory; export those exact bytes, never reread mutable input.
    files = {name: read_regular(source / name, MAX_MANIFEST_BYTES if name.endswith(".json")
                                else MAX_PNG_BYTES) for name in sorted(ALLOWLIST)}
    manifest = validate_manifest(files["capture-manifest.json"])
    dimensions = {}
    for name in CAPTURES:
        try:
            dimensions[name] = png_dimensions(files[name])
        except InvalidCapture as exc:
            # The filename is from CAPTURES, never an untrusted artifact directory entry.
            raise InvalidCapture(f"{name}: {exc}") from exc
    return files, manifest, dimensions


def provenance(manifest, dimensions):
    lines = [
        "# Native iOS simulator captures", "",
        "These are actual iPhone and iPad simulator captures from the compiled iOS app,",
        "exported from the unsigned native-validation artifact. They are not browser substitutes.", "",
        f"- Source repository: `{SOURCE_REPO}`",
        f"- Source commit: `{SOURCE_SHA}`",
        f"- Source workflow run: https://github.com/{SOURCE_REPO}/actions/runs/{SOURCE_RUN}",
        "- Source artifact: `native-ios-screenshots`",
        "- Capture script: `scripts/release/capture-screenshots.py` at the source commit",
        f"- Simulator runtime recorded by the capture script: {manifest['runtime']}", "",
        "| File | Simulator device | Route | Native PNG dimensions |",
        "| --- | --- | --- | --- |",
    ]
    for item in manifest["captures"]:
        width, height = dimensions[item["file"]]
        lines.append(f"| [{item['file']}]({item['file']}) | {item['device']} | "
                     f"`{item['route']}` | {width} × {height} |")
    lines += ["", "## Acceptance still required", "",
              "The manifest and PNG structure have been validated. A human must still open every",
              "image and accept the actual screen, route, layout, safe areas, readable text, and",
              "device dimensions. Export does not establish App Store screenshot acceptance or",
              "native UI correctness. These captures show configure and temperature routes only;",
              "they do not prove active-timer, queue, log, or locked-screen behavior.", "",
              *[f"- {limitation}" for limitation in manifest["limitations"]], "",
              "No signed archive, build log, signing material, or Apple credentials are included.", ""]
    return "\n".join(lines)


def export(source, output, milestone=None):
    files, manifest, dimensions = validate_source(source)
    if milestone:
        milestone("Validator passed: allowlist, manifest, and all four PNG structures match.")
    output = Path(os.path.abspath(output))
    reject_symlink_ancestors(output)
    require(not output.exists(), "Output already exists; refusing to overwrite release evidence")
    output.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".native-captures-", dir=output.parent))
    try:
        for name, content in files.items():
            (staging / name).write_bytes(content)
        (staging / "README.md").write_text(provenance(manifest, dimensions), encoding="utf-8")
        # An existing nonempty directory cannot be replaced by rename.
        require(not output.exists(), "Output appeared during export; refusing to overwrite")
        staging.rename(output)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    if milestone:
        milestone("Export passed: four native PNGs, capture manifest, and provenance README written.")
    return dimensions


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "artifact"
        self.source.mkdir()
        def chunk(kind, payload):
            return (struct.pack(">I", len(payload)) + kind + payload
                    + struct.pack(">I", binascii.crc32(kind + payload) & 0xFFFFFFFF))
        # Real minimal PNG framing with a valid compressed RGB scanline; synthetic test data only.
        self.png = PNG_MAGIC + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
        self.png += chunk(b"IDAT", zlib.compress(b"\0\0\0\0")) + chunk(b"IEND", b"")
        for name in CAPTURES:
            (self.source / name).write_bytes(self.png)
        self.manifest = {"runtime": "iOS 26.2", "captures": [
            {"file": name, "device": "iPhone 17 Pro Max" if family == "iphone" else "iPad Pro 13-inch (M5)",
             "route": route} for name, (family, route) in CAPTURES.items()], "limitations": LIMITATIONS}
        self.write_manifest()

    def write_manifest(self):
        (self.source / "capture-manifest.json").write_text(json.dumps(self.manifest))

    def test_success_exports_only_expected_files_with_provenance(self):
        target = self.root / "release" / "native-screenshots"
        dimensions = export(self.source, target)
        self.assertEqual(set(p.name for p in target.iterdir()), ALLOWLIST | {"README.md"})
        self.assertEqual(dimensions, dict.fromkeys(CAPTURES, (1, 1)))
        self.assertIn(SOURCE_SHA, (target / "README.md").read_text())
        for name in ALLOWLIST:
            self.assertEqual((self.source / name).read_bytes(), (target / name).read_bytes())

    def test_rejects_unexpected_file_without_exporting(self):
        (self.source / "signing.log").write_text("private fixture")
        target = self.root / "output"
        with self.assertRaises(InvalidCapture):
            export(self.source, target)
        self.assertFalse(target.exists())

    def test_rejects_missing_capture(self):
        (self.source / next(iter(CAPTURES))).unlink()
        with self.assertRaises(InvalidCapture):
            validate_source(self.source)

    def test_rejects_symlink(self):
        name = next(iter(CAPTURES))
        (self.root / "outside.png").write_bytes(self.png)
        (self.source / name).unlink()
        (self.source / name).symlink_to(self.root / "outside.png")
        with self.assertRaises(InvalidCapture):
            validate_source(self.source)

    def test_rejects_nested_directory(self):
        (self.source / "archive").mkdir()
        with self.assertRaises(InvalidCapture):
            validate_source(self.source)

    def test_rejects_invalid_png_or_missing_dimensions(self):
        for invalid in (b"not a PNG", PNG_MAGIC, PNG_MAGIC + b"\0" * 12, self.png[:-5], self.png + b"extra"):
            with self.subTest(data=invalid), self.assertRaises(InvalidCapture):
                png_dimensions(invalid)

    def test_rejects_zero_dimensions_and_bad_crc(self):
        invalid = bytearray(self.png)
        invalid[16:20] = b"\0\0\0\0"
        invalid[29:33] = struct.pack(">I", binascii.crc32(invalid[12:29]) & 0xFFFFFFFF)
        with self.assertRaises(InvalidCapture):
            png_dimensions(invalid)
        invalid = bytearray(self.png)
        invalid[29] ^= 1
        with self.assertRaises(InvalidCapture):
            png_dimensions(invalid)

    def test_rejects_manifest_route_filename_device_or_extra_fields(self):
        for field, value in (("route", "file:///private"), ("file", "../secret.png"),
                             ("device", "MacBook Pro"), ("secret", "not exported")):
            original = self.manifest["captures"][0].copy()
            self.manifest["captures"][0][field] = value
            with self.subTest(field=field), self.assertRaises(InvalidCapture):
                validate_manifest(json.dumps(self.manifest).encode())
            self.manifest["captures"][0] = original

    def test_rejects_duplicate_json_keys_and_capture_names(self):
        with self.assertRaises(InvalidCapture):
            validate_manifest(b'{"runtime":"iOS 26.2","runtime":"iOS 26.2"}')
        self.manifest["captures"][1] = self.manifest["captures"][0]
        with self.assertRaises(InvalidCapture):
            validate_manifest(json.dumps(self.manifest).encode())

    def test_refuses_existing_output(self):
        target = self.root / "output"
        target.mkdir()
        marker = target / "user-work.txt"
        marker.write_text("keep")
        with self.assertRaises(InvalidCapture):
            export(self.source, target)
        self.assertEqual(marker.read_text(), "keep")

    def test_rejects_output_symlink_ancestor(self):
        (self.root / "actual").mkdir()
        (self.root / "alias").symlink_to(self.root / "actual", target_is_directory=True)
        with self.assertRaises(InvalidCapture):
            export(self.source, self.root / "alias" / "output")

    def test_annotation_escapes_command_characters(self):
        stream = io.StringIO()
        with patch("sys.stdout", stream):
            annotation("error", "Fixed reason 100%\r\nnext line")
        self.assertEqual(stream.getvalue(),
                         "::error title=Native capture export::Fixed reason 100%25%0D%0Anext line\n")

    def test_filesystem_failure_reason_does_not_include_paths_or_arguments(self):
        error = OSError(13, "sensitive argument", "/private/test-path")
        self.assertEqual(failure_reason(error), "Filesystem operation failed (errno 13)")

    def test_cli_emits_annotation_for_rejected_artifact(self):
        (self.source / "unexpected-secret-name").write_text("sensitive fixture contents")
        stream = io.StringIO()
        errors = io.StringIO()
        arguments = ["export-native-captures.py", "--source", str(self.source),
                     "--output", str(self.root / "output")]
        with patch("sys.argv", arguments), patch("sys.stdout", stream), patch("sys.stderr", errors):
            with self.assertRaises(SystemExit) as result:
                main()
        self.assertEqual(result.exception.code, 1)
        self.assertIn("::error title=Native capture export::Artifact files do not match the allowlist",
                      stream.getvalue())
        for private_value in ("unexpected-secret-name", "sensitive fixture contents", str(self.source)):
            self.assertNotIn(private_value, stream.getvalue() + errors.getvalue())

    def test_success_milestones_are_emitted_only_after_each_completed_stage(self):
        milestones = []
        export(self.source, self.root / "output", milestone=milestones.append)
        self.assertEqual(len(milestones), 2)
        self.assertTrue(milestones[0].startswith("Validator passed:"))
        self.assertTrue(milestones[1].startswith("Export passed:"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, help="Extracted native-ios-screenshots artifact directory")
    parser.add_argument("--output", type=Path, help="New destination directory (must not exist)")
    parser.add_argument("--self-test", action="store_true", help="Run offline validation fixtures only")
    args = parser.parse_args()
    if args.self_test:
        require(args.source is None and args.output is None, "Self-test does not accept source/output")
        result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ExportTests))
        return 0 if result.wasSuccessful() else 1
    parser.error("--source and --output are required") if args.source is None or args.output is None else None
    try:
        dimensions = export(args.source, args.output, milestone=lambda message: annotation("notice", message))
    except (InvalidCapture, OSError) as exc:
        reason = failure_reason(exc)
        annotation("error", reason)
        parser.exit(1, f"Capture export rejected: {reason}\n")
    print(f"Validated and exported {len(dimensions)} native PNGs, capture-manifest.json, and README.md.")
    for name, (width, height) in dimensions.items():
        print(f"{name}: {width} x {height}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
