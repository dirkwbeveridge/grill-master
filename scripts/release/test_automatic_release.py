"""Offline preflight, cryptographic preparation and signed-archive contract tests."""
import base64
from contextlib import redirect_stdout
from datetime import datetime
import importlib.util
import io
import json
import os
from pathlib import Path
import plistlib
import stat
import subprocess
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("automatic_release", Path(__file__).with_name("prepare-automatic-release.py"))
release = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release)


class AutomaticReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workspace = tempfile.TemporaryDirectory()
        cls.root = Path(cls.workspace.name)
        key = cls.root / "fixture-key.pem"
        subprocess.run(["openssl", "genpkey", "-algorithm", "EC", "-pkeyopt", "ec_paramgen_curve:P-256", "-out", str(key)],
                       check=True, capture_output=True)
        cls.private = key.read_bytes()
        cls.bindings = {"ASC_KEY_ID": "KEYID12345", "ASC_ISSUER_ID": "12345678-1234-1234-1234-123456789abc", "APPLE_TEAM_ID": "TEAMID1234"}

    @classmethod
    def tearDownClass(cls):
        cls.workspace.cleanup()

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(dir=self.root)
        self.directory = Path(self.temporary.name)
        self.calls = []
        self.hidden = "private-apple-resource-id"
        self.environment = dict(self.bindings, PATH=os.environ["PATH"], RUNNER_TEMP=str(self.root),
                                ASC_PRIVATE_KEY_P8_BASE64=base64.b64encode(self.private).decode())

    def tearDown(self):
        self.temporary.cleanup()

    def api(self, method, path, query=None, body=None):
        self.calls.append((method, path, query, body))
        self.assertEqual(method, "GET")
        self.assertIsNone(body)
        if path == "/apps":
            self.assertEqual(query["filter[bundleId]"], release.MAIN)
            return {"data": [{"id": self.hidden, "attributes": {"bundleId": release.MAIN}}]}
        if path == "/builds":
            self.assertEqual(query["filter[app]"], self.hidden)
            return {"data": []}
        self.fail("Unexpected API operation")

    def invoke(self, operation="prepare", responder=None, extra=None):
        output = io.StringIO()
        environment = dict(self.environment, **(extra or {}))
        with patch.dict(os.environ, environment, clear=True), patch.object(release.inventory.asc, "request", side_effect=responder or self.api), \
                patch.object(release, "source_version", return_value="3.1"), redirect_stdout(output):
            result = release.main([operation, str(self.directory)])
        rendered = output.getvalue()
        for value in (*self.bindings.values(), self.hidden, str(self.directory), self.private.decode(), environment["ASC_PRIVATE_KEY_P8_BASE64"]):
            self.assertNotIn(value, rendered)
        return result, rendered

    def test_preflight_and_real_es256_key_preparation_without_account_writes(self):
        result, rendered = self.invoke()
        self.assertEqual(result, 0)
        self.assertEqual([call[:2] for call in self.calls], [("GET", "/apps"), ("GET", "/builds")])
        self.assertEqual((self.directory / "AuthKey.p8").read_bytes(), self.private)
        for path in self.directory.iterdir():
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
        options = plistlib.loads((self.directory / "ExportOptions.plist").read_bytes())
        self.assertEqual(options["method"], "app-store-connect")
        self.assertEqual(options["destination"], "upload")
        self.assertEqual(options["signingStyle"], "automatic")
        self.assertFalse(options["manageAppVersionAndBuildNumber"])
        self.assertFalse(options["testFlightInternalTestingOnly"])
        self.assertNotIn("provisioningProfiles", options)
        self.assertNotIn("signingCertificate", options)
        self.assertEqual(json.loads((self.directory / "expected.json").read_text())["build"], "2")
        self.assertFalse(list(self.root.glob("grillmaster-apple-inventory-*")))
        self.assertIn("unused build number", rendered)

    def test_missing_app_stops_before_writing_any_release_inputs(self):
        def missing(method, path, query=None, body=None):
            self.calls.append((method, path, query, body))
            return {"data": []}
        result, rendered = self.invoke(responder=missing)
        self.assertEqual(result, 1)
        self.assertIn("exact main app record must exist", rendered)
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(list(self.directory.iterdir()), [])

    def test_wrong_app_identifier_never_used_for_build_query(self):
        def wrong(method, path, query=None, body=None):
            self.calls.append((method, path, query, body))
            return {"data": [{"id": self.hidden, "attributes": {"bundleId": "com.unrelated.blueberry"}}]}
        result, _ = self.invoke(responder=wrong)
        self.assertEqual(result, 1)
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(list(self.directory.iterdir()), [])

    def test_existing_build_rejected_before_archive_inputs_are_written(self):
        def duplicate(method, path, query=None, body=None):
            response = self.api(method, path, query, body)
            return {"data": [{"id": self.hidden}]} if path == "/builds" else response
        result, rendered = self.invoke(responder=duplicate, extra={"BUILD_NUMBER": "27"})
        self.assertEqual(result, 1)
        self.assertIn("already contains this build number", rendered)
        self.assertEqual(self.calls[-1][2]["filter[version]"], "27")
        self.assertEqual(list(self.directory.iterdir()), [])

    def test_authentication_failure_is_sanitized_and_keeps_no_material(self):
        def unauthorized(*args, **kwargs):
            raise RuntimeError("HTTP 401 " + self.hidden + " raw-private-api-body")
        result, rendered = self.invoke(responder=unauthorized)
        self.assertEqual(result, 1)
        self.assertIn("authentication was rejected", rendered)
        self.assertNotIn("raw-private-api-body", rendered)
        self.assertEqual(list(self.directory.iterdir()), [])

    def test_key_failure_before_api_leaves_no_files(self):
        result, rendered = self.invoke(extra={"ASC_PRIVATE_KEY_P8_BASE64": "invalid-private-key-input"})
        self.assertEqual(result, 1)
        self.assertIn("Credential validation failed", rendered)
        self.assertEqual(self.calls, [])
        self.assertEqual(list(self.directory.iterdir()), [])

    def test_invalid_build_or_notes_fail_before_api(self):
        for extra in ({"BUILD_NUMBER": "0"}, {"BUILD_NUMBER": "1;touch /private/path"}, {"TESTFLIGHT_WHATS_NEW": " "}):
            with self.subTest(input_category=next(iter(extra))):
                result, _ = self.invoke(extra=extra)
                self.assertEqual(result, 1)
                self.assertEqual(self.calls, [])
                self.assertEqual(list(self.directory.iterdir()), [])

    def test_generated_shell_configuration_quotes_notes_as_data(self):
        marker = self.directory / "must-not-exist"
        notes = f"Timer checks'; touch {marker}; # $(touch {marker}) `touch {marker}`"
        result, _ = self.invoke(extra={"TESTFLIGHT_WHATS_NEW": notes, "ASC_KEY_ID": " \t" + self.bindings["ASC_KEY_ID"] + "\n"})
        self.assertEqual(result, 0)
        subprocess.run(["bash", "-c", 'set -eu; source "$1"; test "$BUILD_NUMBER" = 2', "test", str(self.directory / "auth.env")],
                       check=True, capture_output=True)
        self.assertFalse(marker.exists())
        self.assertIn("export ASC_KEY_ID=" + self.bindings["ASC_KEY_ID"] + "\n", (self.directory / "auth.env").read_text())

    def test_partial_write_failure_removes_new_files_preserves_existing(self):
        existing = self.directory / "auth.env"
        existing.write_text("preserve-existing-data")
        result, _ = self.invoke()
        self.assertEqual(result, 1)
        self.assertEqual(existing.read_text(), "preserve-existing-data")
        self.assertFalse((self.directory / "AuthKey.p8").exists())

    def test_insecure_directory_rejected_before_key_or_api(self):
        self.directory.chmod(0o755)
        result, rendered = self.invoke()
        self.assertEqual(result, 1)
        self.assertIn("private, owned directory", rendered)
        self.assertEqual(self.calls, [])


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.directory = Path(self.temporary.name)
        self.expected = {"team": "TEAMID1234", "build": "2", "version": "3.1"}
        (self.directory / "expected.json").write_text(json.dumps(self.expected))
        self.app = self.directory / "App.xcarchive/Products/Applications/App.app"
        self.widget = self.app / "PlugIns/GrillMasterWidgets.appex"
        self.widget.mkdir(parents=True)
        self.signed_groups = [release.GROUP]
        self.profile_groups = [release.GROUP]
        for bundle, identifier in ((self.app, release.MAIN), (self.widget, release.WIDGET)):
            (bundle / "Info.plist").write_bytes(plistlib.dumps({"CFBundleIdentifier": identifier,
                "CFBundleVersion": "2", "CFBundleShortVersionString": "3.1", "ITSAppUsesNonExemptEncryption": False}))
            (bundle / "embedded.mobileprovision").write_bytes(b"private-profile-fixture")

    def tearDown(self):
        self.temporary.cleanup()

    def native(self, *args):
        path = Path(args[-1])
        bundle = path.parent if args[0] == "security" else path
        identifier = plistlib.loads((bundle / "Info.plist").read_bytes())["CFBundleIdentifier"]
        signed = {"application-identifier": "LEGACY1234." + identifier,
                  "com.apple.developer.team-identifier": self.expected["team"],
                  "com.apple.security.application-groups": self.signed_groups}
        if args[0] == "codesign":
            return b"" if args[1] == "--verify" else plistlib.dumps(signed)
        profile = {"ApplicationIdentifierPrefix": ["LEGACY1234"], "TeamIdentifier": [self.expected["team"]],
                   "ExpirationDate": datetime(2099, 1, 1), "Entitlements": dict(signed)}
        profile["Entitlements"]["com.apple.security.application-groups"] = self.profile_groups
        return plistlib.dumps(profile)

    def verify(self):
        output = io.StringIO()
        with patch.object(release, "command", side_effect=self.native), redirect_stdout(output):
            result = release.main(["verify-archive", str(self.directory)])
        rendered = output.getvalue()
        self.assertNotIn(self.expected["team"], rendered)
        self.assertNotIn(str(self.directory), rendered)
        return result, rendered

    def test_both_actual_bundle_plists_signatures_profiles_and_entitlements_checked(self):
        result, rendered = self.verify()
        self.assertEqual(result, 0)
        self.assertIn("Archive verified", rendered)

    def test_signed_group_mismatch_blocks_upload(self):
        self.signed_groups = ["group.unrelated.app"]
        result, rendered = self.verify()
        self.assertEqual(result, 1)
        self.assertIn("signed App Group/team entitlement is invalid", rendered)

    def test_embedded_profile_group_mismatch_blocks_upload(self):
        self.profile_groups = []
        result, rendered = self.verify()
        self.assertEqual(result, 1)
        self.assertIn("embedded provisioning profile", rendered)

    def test_extension_build_mismatch_blocks_upload(self):
        path = self.widget / "Info.plist"
        info = plistlib.loads(path.read_bytes())
        info["CFBundleVersion"] = "1"
        path.write_bytes(plistlib.dumps(info))
        result, _ = self.verify()
        self.assertEqual(result, 1)

    def test_nonexempt_encryption_declaration_cannot_pass_archive_gate(self):
        path = self.app / "Info.plist"
        info = plistlib.loads(path.read_bytes())
        info["ITSAppUsesNonExemptEncryption"] = True
        path.write_bytes(plistlib.dumps(info))
        result, _ = self.verify()
        self.assertEqual(result, 1)

    def test_missing_profile_cannot_pass_archive_gate(self):
        (self.widget / "embedded.mobileprovision").unlink()
        result, _ = self.verify()
        self.assertEqual(result, 1)


class SafeDiagnosisTests(unittest.TestCase):
    def test_private_logs_produce_only_fixed_failure_categories(self):
        cases = [("Your team has no devices from which to generate a provisioning profile.", "development-device registration"),
                 ("You have reached the maximum number of certificates for this account.", "certificate quota"),
                 ("error: profile doesn't include the application-groups entitlement", "App Group association"),
                 ("authentication failed HTTP 403", "authentication or authorization"),
                 ("CFBundleVersion has already been used", "duplicate or invalid build number")]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "private-log.txt"
            for log, category in cases:
                with self.subTest(category=category):
                    path.write_text(log + " private-operational-value /private/secret/key.p8 RAW_PRIVATE_BODY")
                    output = io.StringIO()
                    with redirect_stdout(output):
                        release.diagnose(path, "archive")
                    rendered = output.getvalue()
                    self.assertIn(category, rendered)
                    for hidden in ("private-operational-value", "/private/secret/key.p8", "RAW_PRIVATE_BODY", log):
                        self.assertNotIn(hidden, rendered)


if __name__ == "__main__":
    unittest.main()
