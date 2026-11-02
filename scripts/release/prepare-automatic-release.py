#!/usr/bin/env python3
"""Prepare and verify one automatic-signing TestFlight release without logging secrets.

Commands: prepare DIRECTORY; verify-archive DIRECTORY; diagnose LOG STAGE;
snapshot-profiles DIRECTORY; cleanup-profiles DIRECTORY. All material is private
and outside the checkout. No account write is performed by this Python helper.
"""
import argparse
from datetime import datetime, timezone
import importlib.util
import json
import os
from pathlib import Path
import plistlib
import re
import shlex
import stat
import subprocess

SPEC = importlib.util.spec_from_file_location("automatic_inventory", Path(__file__).with_name("check-apple-access.py"))
inventory = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(inventory)

ROOT = Path(__file__).resolve().parents[2]
MAIN = "com.dbeveridge.grillmaster"
WIDGET = MAIN + ".widgets"
GROUP = "group.com.dbeveridge.grillmaster"
DEFAULT_NOTES = "Validate cooking timers, background reminders, Live Activities, and iPhone/iPad layouts."
MESSAGES = {
    "unsafe_directory": "Release files require a private, owned directory outside the checkout.",
    "invalid_build": "Build number must be a positive integer.",
    "invalid_notes": "What to Test must contain 1–4000 characters.",
    "source_version": "The source marketing versions are missing or inconsistent.",
    "missing_app": "Preflight stopped: the exact main app record must exist in App Store Connect before automatic signing or upload.",
    "duplicate_build": "Preflight stopped: App Store Connect already contains this build number. Choose a new build number before archiving.",
    "authentication_failed": "Preflight authentication was rejected by Apple. Verify the API key binding privately.",
    "permission_denied": "Preflight read permission was denied by Apple. Verify app access privately.",
    "request_failed": "Preflight API request failed; app existence and build uniqueness remain unverified.",
    "credential_failed": "Credential validation failed. Run the read-only Apple inventory for a sanitized input-stage diagnosis.",
    "archive_invalid": "Archive verification failed: app/extension contents, identifiers, marketing versions, build numbers, or encryption declarations do not match.",
    "signature_invalid": "Archive verification failed: a code signature or signed App Group/team entitlement is invalid.",
    "profile_invalid": "Archive verification failed: an embedded provisioning profile is missing, expired, or lacks the expected app, team, or App Group.",
    "generic": "Automatic release operation failed safely; no private diagnostic values were disclosed.",
}


class ReleaseError(Exception):
    def __init__(self, kind):
        self.kind = kind


def emit(message, level="notice"):
    # Callers supply only fixed messages, never exception text or API/log values.
    print(f"::{level} title=Automatic TestFlight::{message}")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        try:
            with open(summary, "a", encoding="utf-8") as stream:
                stream.write(f"- {message}\n")
        except OSError:
            print("::warning title=Automatic TestFlight::Step summary could not be written; sanitized annotations remain available.")


def private_directory(value):
    try:
        directory = Path(value).resolve(strict=True)
        metadata = directory.stat()
        if (not directory.is_dir() or directory == ROOT or ROOT in directory.parents
                or metadata.st_uid != os.getuid() or stat.S_IMODE(metadata.st_mode) != 0o700):
            raise ReleaseError("unsafe_directory")
        return directory
    except OSError:
        raise ReleaseError("unsafe_directory") from None


def write_private(path, data):
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
    except Exception:
        path.unlink(missing_ok=True)
        raise


def get_all(path, query):
    try:
        return inventory.all_pages(path, query)[0]
    except inventory.InventoryError as error:
        raise ReleaseError(error.kind if error.kind in {"authentication_failed", "permission_denied"} else "request_failed") from None


def preflight(build):
    apps = get_all("/apps", {"filter[bundleId]": MAIN, "fields[apps]": "bundleId", "limit": "2"})
    if (len(apps) != 1 or apps[0].get("attributes", {}).get("bundleId") != MAIN
            or not isinstance(apps[0].get("id"), str) or not apps[0]["id"]):
        raise ReleaseError("missing_app")
    builds = get_all("/builds", {"filter[app]": apps[0]["id"], "filter[version]": build, "limit": "2"})
    if builds:
        raise ReleaseError("duplicate_build")


def source_version():
    source = (ROOT / "ios/App/App.xcodeproj/project.pbxproj").read_text()
    versions = set(re.findall(r'\bMARKETING_VERSION\s*=\s*"?([0-9]+(?:\.[0-9]+){0,2})"?\s*;', source))
    if len(versions) != 1:
        raise ReleaseError("source_version")
    return versions.pop()


def prepare(value):
    directory = private_directory(value)
    build = os.environ.get("BUILD_NUMBER", "2")
    notes = os.environ.get("TESTFLIGHT_WHATS_NEW", DEFAULT_NOTES)
    if not re.fullmatch(r"[1-9][0-9]*", build):
        raise ReleaseError("invalid_build")
    if not notes.strip() or len(notes) > 4000:
        raise ReleaseError("invalid_notes")
    version = source_version()
    created = []
    try:
        # This context validates identifier formats, P-256 key material, and ES256
        # signing. Copy the validated key before its short-lived context ends.
        with inventory.credentials():
            preflight(build)
            values = {name: os.environ[name] for name in ("ASC_KEY_ID", "ASC_ISSUER_ID", "APPLE_TEAM_ID")}
            values.update({"ASC_KEY_PATH": str(directory / "AuthKey.p8"), "BUILD_NUMBER": build,
                           "EXPECTED_MARKETING_VERSION": version, "TESTFLIGHT_WHATS_NEW": notes})
            options = {"method": "app-store-connect", "destination": "upload", "signingStyle": "automatic",
                       "teamID": values["APPLE_TEAM_ID"], "manageAppVersionAndBuildNumber": False,
                       "testFlightInternalTestingOnly": False, "uploadSymbols": True, "stripSwiftSymbols": True}
            expected = {"team": values["APPLE_TEAM_ID"], "build": build, "version": version}
            files = {"AuthKey.p8": Path(os.environ["ASC_KEY_PATH"]).read_bytes(),
                     "auth.env": "".join(f"export {name}={shlex.quote(value)}\n" for name, value in values.items()).encode(),
                     "ExportOptions.plist": plistlib.dumps(options), "expected.json": json.dumps(expected).encode()}
            for name, data in files.items():
                path = directory / name
                write_private(path, data)
                created.append(path)
    except inventory.InventoryError:
        for path in created:
            path.unlink(missing_ok=True)
        raise ReleaseError("credential_failed") from None
    except Exception:
        for path in created:
            path.unlink(missing_ok=True)
        raise
    emit("Preflight verified the exact App Store Connect app and an unused build number; protected automatic-signing inputs are prepared.")


def command(*args):
    try:
        return subprocess.run(args, check=True, capture_output=True, timeout=60).stdout
    except (OSError, subprocess.SubprocessError):
        raise ReleaseError("signature_invalid") from None


def load_plist(path, error="archive_invalid"):
    try:
        return plistlib.loads(path.read_bytes())
    except (OSError, ValueError, plistlib.InvalidFileException):
        raise ReleaseError(error) from None


def verify_bundle(bundle, identifier, expected):
    info = load_plist(bundle / "Info.plist")
    if (info.get("CFBundleIdentifier") != identifier or info.get("CFBundleVersion") != expected["build"]
            or info.get("CFBundleShortVersionString") != expected["version"]
            or info.get("ITSAppUsesNonExemptEncryption") is not False):
        raise ReleaseError("archive_invalid")
    command("codesign", "--verify", "--strict", "--verbose=0", str(bundle))
    try:
        signed = plistlib.loads(command("codesign", "-d", "--entitlements", ":-", str(bundle)))
    except (ValueError, plistlib.InvalidFileException):
        raise ReleaseError("signature_invalid") from None
    if (signed.get("com.apple.developer.team-identifier") != expected["team"]
            or GROUP not in signed.get("com.apple.security.application-groups", [])):
        raise ReleaseError("signature_invalid")
    profile_path = bundle / "embedded.mobileprovision"
    if not profile_path.is_file():
        raise ReleaseError("profile_invalid")
    try:
        profile = plistlib.loads(command("security", "cms", "-D", "-i", str(profile_path)))
        entitlements = profile["Entitlements"]
        expiration = profile["ExpirationDate"]
        if expiration.tzinfo is None:
            expiration = expiration.replace(tzinfo=timezone.utc)
        prefixes = profile["ApplicationIdentifierPrefix"]
        application = entitlements.get("application-identifier")
        if (expected["team"] not in profile["TeamIdentifier"] or expiration <= datetime.now(timezone.utc)
                or entitlements.get("com.apple.developer.team-identifier") != expected["team"]
                or GROUP not in entitlements.get("com.apple.security.application-groups", [])
                or application not in {f"{prefix}.{identifier}" for prefix in prefixes}
                or signed.get("application-identifier") != application):
            raise ReleaseError("profile_invalid")
    except ReleaseError:
        raise ReleaseError("profile_invalid") from None
    except Exception:
        raise ReleaseError("profile_invalid") from None


def verify_archive(value):
    directory = private_directory(value)
    expected = json.loads((directory / "expected.json").read_text())
    apps = list((directory / "App.xcarchive/Products/Applications").glob("*.app"))
    if len(apps) != 1:
        raise ReleaseError("archive_invalid")
    extensions = list((apps[0] / "PlugIns").glob("*.appex"))
    if len(extensions) != 1:
        raise ReleaseError("archive_invalid")
    verify_bundle(apps[0], MAIN, expected)
    verify_bundle(extensions[0], WIDGET, expected)
    emit("Archive verified: app and widget identifiers, marketing version, build number, exempt encryption, signatures, embedded profiles, and signed team/App Group entitlements match.")


def profile_directories():
    return (Path.home() / "Library/MobileDevice/Provisioning Profiles",
            Path.home() / "Library/Developer/Xcode/UserData/Provisioning Profiles")


def snapshot_profiles(value):
    directory = private_directory(value)
    existing = [str(path.resolve()) for root in profile_directories() if root.is_dir()
                for path in root.glob("*.mobileprovision") if path.is_file()]
    write_private(directory / "original-profiles.json", json.dumps(existing).encode())


def cleanup_profiles(value):
    directory = private_directory(value)
    snapshot = directory / "original-profiles.json"
    if not snapshot.is_file():
        return
    existing = set(json.loads(snapshot.read_text()))
    team = os.environ.get("APPLE_TEAM_ID", "").strip()
    for root in profile_directories():
        if not root.is_dir():
            continue
        for path in root.glob("*.mobileprovision"):
            if not path.is_file() or str(path.resolve()) in existing:
                continue
            try:
                profile = plistlib.loads(command("security", "cms", "-D", "-i", str(path)))
                identifier = profile.get("Entitlements", {}).get("application-identifier", "")
                prefixes = profile.get("ApplicationIdentifierPrefix", [])
                if team in profile.get("TeamIdentifier", []) and identifier in {f"{prefix}.{bundle}" for prefix in prefixes for bundle in (MAIN, WIDGET)}:
                    path.unlink()
            except Exception:
                emit("A newly installed profile could not be safely identified for cleanup; no existing or unrelated profile was removed.", "warning")


def diagnose(log, stage):
    try:
        text = Path(log).read_text(errors="replace").lower()
    except OSError:
        text = ""
    if stage == "keychain":
        emit("The isolated signing keychain could not be configured. No archive/upload was attempted; private keychain diagnostics were not published.", "error")
        return
    checks = (
        (r"no (?:registered )?devices|team has no devices|doesn.t include any devices", "Automatic provisioning requires development-device registration. No device was registered; resolve the signing configuration before another attempt."),
        (r"maximum number.{0,100}certificat|certificate.{0,100}quota|already has.{0,100}distribution certificates|limit.{0,80}distribution certificat", "Apple's signing certificate quota blocked automatic signing. No certificate was revoked; resolve certificate ownership or quota before another attempt."),
        (r"(?:error:|doesn.t|does not|not support|not include|missing|mismatch|failed).{0,180}(?:app group|application-groups)|(?:app group|application-groups).{0,180}(?:not registered|not available|not supported|missing|mismatch)", "The required App Group association or entitlement is unavailable to automatic signing. Resolve both app and widget App Group membership before another attempt."),
        (r"unable to authenticate|authentication.{0,60}failed|not authorized|http (?:401|403)|invalid.{0,50}api key", "Apple authentication or authorization blocked automatic signing/upload. Verify the key's access privately before another attempt."),
        (r"cfbundleversion.{0,100}(?:already|must)|bundle version.{0,100}already|duplicate.{0,30}build|redundant binary", "Apple rejected a duplicate or invalid build number. Check App Store Connect before choosing a new build number."),
        (r"no signing certificate|signing certificate.{0,80}not found|private key.{0,50}missing", "An accessible signing certificate/private key was unavailable. Automatic signing was attempted once; no certificate was revoked."),
        (r"no profiles for|provisioning profile.{0,100}(?:doesn.t|does not|not support|not include|expired)", "Automatic provisioning could not supply a compatible profile. Resolve capabilities and signing access before another attempt."),
        (r"connection.{0,60}(?:failed|timed out)|network.{0,50}(?:unreachable|lost)|ssl.{0,40}error|tls.{0,40}error", "A network or TLS error interrupted signing/upload. Check Apple state before another attempt; normal TLS verification remains enabled."),
    )
    message = next((message for pattern, message in checks if re.search(pattern, text)),
                   "Xcode failed during archive or upload. Private logs were not published; resolve the project/signing failure on a trusted Mac before another attempt.")
    emit(message, "error")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="operation", required=True)
    for operation in ("prepare", "verify-archive", "snapshot-profiles", "cleanup-profiles"):
        sub.add_parser(operation).add_argument("directory")
    diagnostic = sub.add_parser("diagnose")
    diagnostic.add_argument("log")
    diagnostic.add_argument("stage", choices=("archive", "export", "keychain"))
    args = parser.parse_args(argv)
    try:
        if args.operation == "diagnose":
            diagnose(args.log, args.stage)
        else:
            {"prepare": prepare, "verify-archive": verify_archive, "snapshot-profiles": snapshot_profiles,
             "cleanup-profiles": cleanup_profiles}[args.operation](args.directory)
    except ReleaseError as error:
        emit(MESSAGES.get(error.kind, MESSAGES["generic"]), "error")
        return 1
    except Exception:
        emit(MESSAGES["generic"], "error")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
