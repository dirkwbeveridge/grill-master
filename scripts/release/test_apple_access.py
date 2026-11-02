"""Offline inventory safety contracts; no requests to Apple and no persistent keys."""
import base64
from contextlib import redirect_stdout
import importlib.util
import io
import os
from pathlib import Path
import stat
import subprocess
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("apple_access", Path(__file__).with_name("check-apple-access.py"))
inventory = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(inventory)


class InventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workspace = tempfile.TemporaryDirectory()
        cls.root = Path(cls.workspace.name)
        key = cls.root / "fixture-source.pem"
        subprocess.run(["openssl", "genpkey", "-algorithm", "EC", "-pkeyopt", "ec_paramgen_curve:P-256", "-out", str(key)],
                       check=True, capture_output=True)
        cls.private = key.read_bytes()
        cls.environment = {"ASC_KEY_ID": "KEYID12345", "ASC_ISSUER_ID": "12345678-1234-1234-1234-123456789abc",
                           "APPLE_TEAM_ID": "TEAMID1234", "ASC_PRIVATE_KEY_P8_BASE64": base64.b64encode(cls.private).decode(),
                           "RUNNER_TEMP": str(cls.root)}

    @classmethod
    def tearDownClass(cls):
        cls.workspace.cleanup()

    def setUp(self):
        self.secret_id = "private-resource-id-do-not-print"
        self.bundle_ids = {label: self.secret_id + label.replace(" ", "") for label in inventory.BUNDLES}
        self.methods = []

    def fake_request(self, method, path, query=None, body=None):
        self.methods.append(method)
        self.assertEqual(method, "GET")
        self.assertIsNone(body)
        if path == "/apps":
            return {"data": [{"id": self.secret_id, "attributes": {"bundleId": inventory.BUNDLES["Main app"]}}]}
        if path == "/bundleIds":
            label = next(label for label, identifier in inventory.BUNDLES.items() if identifier == query["filter[identifier]"])
            return {"data": [{"id": self.bundle_ids[label], "attributes": {"identifier": inventory.BUNDLES[label]}}]}
        if path.endswith("/bundleIdCapabilities"):
            return {"data": [{"id": self.secret_id, "attributes": {"capabilityType": "APP_GROUPS"}}]}
        if path == "/certificates":
            return {"data": [{"id": self.secret_id, "attributes": {"certificateType": "DISTRIBUTION", "expirationDate": "2099-01-01T00:00:00Z"}}]}
        if path == "/profiles":
            self.assertEqual(query["include"], "bundleId,certificates")
            return {"data": [{"id": self.secret_id, "attributes": {"profileType": "IOS_APP_STORE", "profileState": "ACTIVE",
                                                                   "expirationDate": "2099-01-01T00:00:00Z"},
                              "relationships": {"bundleId": {"data": {"id": value}}}} for value in self.bundle_ids.values()]}
        self.fail("Unexpected request")

    def invoke(self, responder=None, extra=None):
        environment = dict(self.environment, **(extra or {}))
        output = io.StringIO()
        with patch.dict(os.environ, environment), patch.object(inventory.asc, "request", side_effect=responder or self.fake_request), redirect_stdout(output):
            result = inventory.main()
        rendered = output.getvalue()
        for secret in (self.secret_id, environment["ASC_KEY_ID"], environment["ASC_ISSUER_ID"], environment["APPLE_TEAM_ID"],
                       environment["ASC_PRIVATE_KEY_P8_BASE64"], str(self.root), self.private.decode()):
            self.assertNotIn(secret, rendered)
        return result, rendered

    def test_present_inventory_is_read_only_and_sanitized_with_summary(self):
        summary = self.root / "summary.md"
        result, rendered = self.invoke(extra={"GITHUB_STEP_SUMMARY": str(summary)})
        self.assertEqual(result, 0)
        self.assertIn("API authentication | Accepted", rendered)
        self.assertIn("Unexpired distribution certificates | 1", rendered)
        self.assertIn("Main app active App Store profiles | 1", rendered)
        self.assertIn("::notice title=Apple signing inventory::", rendered)
        self.assertIn("group membership unverified", rendered)
        self.assertIn("Read permission does not prove", summary.read_text())
        self.assertNotIn(self.secret_id, summary.read_text())
        self.assertTrue(all(method == "GET" for method in self.methods))
        self.assertFalse(list(self.root.glob("grillmaster-apple-inventory-*")))
        summary.unlink()

    def test_missing_app_does_not_skip_identifier_or_certificate_inventory(self):
        def missing(method, path, query=None, body=None):
            if path in {"/apps", "/certificates", "/profiles"}:
                self.methods.append(method)
                return {"data": []}
            return self.fake_request(method, path, query, body)
        result, rendered = self.invoke(missing)
        self.assertEqual(result, 2)
        self.assertIn("API authentication | Accepted", rendered)
        self.assertIn("App Store Connect app | Missing", rendered)
        self.assertIn("Unexpired distribution certificates | 0", rendered)
        self.assertIn("Main app identifier | Present", rendered)
        self.assertIn("Widget extension active App Store profiles | 0", rendered)

    def test_authentication_failure_is_not_reported_as_missing_app(self):
        def rejected(*args, **kwargs):
            raise RuntimeError("HTTP 401 raw-body=" + self.secret_id)
        result, rendered = self.invoke(rejected)
        self.assertEqual(result, 1)
        self.assertIn("Authentication rejected (HTTP 401)", rendered)
        self.assertNotIn("App Store Connect app | Missing", rendered)

    def test_profile_endpoint_unavailable_is_unknown_not_absence(self):
        def unavailable(method, path, query=None, body=None):
            if path == "/profiles":
                raise RuntimeError("HTTP 404 " + self.secret_id)
            return self.fake_request(method, path, query, body)
        result, rendered = self.invoke(unavailable)
        self.assertEqual(result, 2)
        self.assertIn("App Store profile inventory | Endpoint unavailable", rendered)
        self.assertNotIn("active App Store profiles | 0", rendered)

    def test_permission_denial_is_distinct_and_other_inventory_continues(self):
        def denied(method, path, query=None, body=None):
            if path == "/apps":
                raise RuntimeError("HTTP 403 " + self.secret_id)
            return self.fake_request(method, path, query, body)
        result, rendered = self.invoke(denied)
        self.assertEqual(result, 1)
        self.assertIn("Read access denied (HTTP 403)", rendered)
        self.assertIn("Unexpired distribution certificates | 1", rendered)

    def test_arbitrary_api_exception_never_leaks_values(self):
        def broken(*args, **kwargs):
            raise RuntimeError(self.secret_id + self.environment["ASC_PRIVATE_KEY_P8_BASE64"])
        result, rendered = self.invoke(broken)
        self.assertEqual(result, 1)
        self.assertIn("Request failed; inventory unknown", rendered)

    def test_malformed_key_is_rejected_before_api(self):
        result, rendered = self.invoke(extra={"ASC_PRIVATE_KEY_P8_BASE64": "%%%not-valid-base64%%%"})
        self.assertEqual(result, 1)
        self.assertFalse(self.methods)
        self.assertIn("API private key input is malformed", rendered)

    def test_wrong_curve_is_rejected_and_key_directory_removed(self):
        key = self.root / "wrong-curve.pem"
        subprocess.run(["openssl", "genpkey", "-algorithm", "EC", "-pkeyopt", "ec_paramgen_curve:P-384", "-out", str(key)],
                       check=True, capture_output=True)
        result, _ = self.invoke(extra={"ASC_PRIVATE_KEY_P8_BASE64": base64.b64encode(key.read_bytes()).decode()})
        self.assertEqual(result, 1)
        self.assertFalse(self.methods)
        self.assertFalse(list(self.root.glob("grillmaster-apple-inventory-*")))
        key.unlink()

    def test_malformed_pkcs8_pem_does_not_log_openssl_diagnostics(self):
        malformed = b"-----BEGIN PRIVATE KEY-----\nprivate-invalid-key-content\n-----END PRIVATE KEY-----\n"
        result, rendered = self.invoke(extra={"ASC_PRIVATE_KEY_P8_BASE64": base64.b64encode(malformed).decode()})
        self.assertEqual(result, 1)
        self.assertNotIn("private-invalid-key-content", rendered)
        self.assertFalse(self.methods)
        self.assertFalse(list(self.root.glob("grillmaster-apple-inventory-*")))

    def test_protected_key_and_environment_restoration_after_failure(self):
        with patch.dict(os.environ, dict(self.environment, ASC_KEY_PATH="prior-private-path")):
            with self.assertRaises(RuntimeError):
                with inventory.credentials():
                    path = Path(os.environ["ASC_KEY_PATH"])
                    self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
                    self.assertEqual(stat.S_IMODE(path.parent.stat().st_mode), 0o700)
                    self.assertEqual(path.read_bytes(), self.private)
                    raise RuntimeError("simulated interruption")
            self.assertEqual(os.environ["ASC_KEY_PATH"], "prior-private-path")
            self.assertFalse(path.exists())

    def test_pagination_stays_on_apple_api_origin(self):
        responses = [{"data": [{"id": self.secret_id}], "links": {"next": "https://api.appstoreconnect.apple.com/v1/certificates?cursor=private-cursor"}},
                     {"data": []}]
        with patch.object(inventory.asc, "request", side_effect=responses) as request:
            data, _ = inventory.all_pages("/certificates")
        self.assertEqual(len(data), 1)
        self.assertEqual(request.call_args_list[1].args, ("GET", "/certificates"))
        self.assertEqual(request.call_args_list[1].kwargs["query"], {"cursor": "private-cursor"})
        with patch.object(inventory.asc, "request", return_value={"data": [], "links": {"next": "https://attacker.invalid/v1/certificates"}}):
            with self.assertRaises(inventory.InventoryError):
                inventory.all_pages("/certificates")

    def test_invalid_issuer_is_rejected_without_echo(self):
        result, rendered = self.invoke(extra={"ASC_ISSUER_ID": "invalid-sensitive-issuer"})
        self.assertEqual(result, 1)
        self.assertIn("input format is invalid", rendered)
        self.assertFalse(self.methods)


if __name__ == "__main__":
    unittest.main()
