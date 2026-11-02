"""Offline scope, idempotency, uncertain-write recovery and safe-output tests."""
from contextlib import nullcontext, redirect_stdout
import copy
import importlib.util
import io
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("ensure_identifiers", Path(__file__).with_name("ensure-apple-identifiers.py"))
ensure = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ensure)


class ProvisionTests(unittest.TestCase):
    def setUp(self):
        self.bundles = {}
        self.capabilities = {}
        self.calls = []
        self.hidden = "private-operational-value-never-output"
        self.unrelated = {"identifier": "com.unrelated.blueberry", "certificates": ["preserve"], "capabilities": ["PUSH_NOTIFICATIONS"]}
        self.saved_unrelated = copy.deepcopy(self.unrelated)

    def resource(self, identifier):
        return {"type": "bundleIds", "id": self.bundles[identifier], "attributes": {"identifier": identifier, "platform": "IOS"}}

    def fake(self, method, path, query=None, body=None):
        self.calls.append((method, path, query, copy.deepcopy(body)))
        if method == "GET" and path == "/bundleIds":
            identifier = query["filter[identifier]"]
            self.assertIn(identifier, {target[1] for target in ensure.TARGETS})
            return {"data": [self.resource(identifier)] if identifier in self.bundles else []}
        if method == "GET" and path.endswith("/bundleIdCapabilities"):
            resource_id = path.split("/")[2]
            self.assertIn(resource_id, self.bundles.values())
            return {"data": [{"type": "bundleIdCapabilities", "id": self.hidden,
                              "attributes": {"capabilityType": capability}} for capability in self.capabilities.get(resource_id, [])]}
        if method == "POST" and path == "/bundleIds":
            attributes = body["data"]["attributes"]
            identifier = attributes["identifier"]
            target = next(target for target in ensure.TARGETS if target[1] == identifier)
            self.assertEqual(attributes, {"name": target[2], "identifier": target[1], "platform": "IOS"})
            self.assertNotIn(identifier, self.bundles)
            self.bundles[identifier] = self.hidden + str(len(self.bundles))
            return {"data": self.resource(identifier)}
        if method == "POST" and path == "/bundleIdCapabilities":
            data = body["data"]
            self.assertEqual(data["type"], "bundleIdCapabilities")
            self.assertEqual(data["attributes"], {"capabilityType": "APP_GROUPS", "settings": []})
            resource_id = data["relationships"]["bundleId"]["data"]["id"]
            self.assertIn(resource_id, self.bundles.values())
            self.capabilities.setdefault(resource_id, []).append("APP_GROUPS")
            return {"data": {"type": "bundleIdCapabilities", "id": self.hidden, "attributes": {"capabilityType": "APP_GROUPS"}}}
        self.fail("Unexpected API mutation or endpoint")

    def existing(self, groups=True):
        for index, target in enumerate(ensure.TARGETS):
            resource_id = self.hidden + str(index)
            self.bundles[target[1]] = resource_id
            self.capabilities[resource_id] = ["ASSOCIATED_DOMAINS", "PUSH_NOTIFICATIONS"] + (["APP_GROUPS"] if groups else [])

    def invoke(self, responder=None, summary=None):
        output = io.StringIO()
        environment = {"GITHUB_STEP_SUMMARY": str(summary)} if summary else {}
        with patch.object(ensure.inventory, "credentials", return_value=nullcontext()), \
                patch.object(ensure.inventory.asc, "request", side_effect=responder or self.fake), \
                patch.dict(os.environ, environment), redirect_stdout(output):
            result = ensure.main()
        rendered = output.getvalue()
        self.assertNotIn(self.hidden, rendered)
        self.assertNotIn("raw-private-error-body", rendered)
        self.assertNotIn("com.unrelated.blueberry", rendered)
        self.assertEqual(self.unrelated, self.saved_unrelated)
        self.assertTrue(all(call[0] in {"GET", "POST"} for call in self.calls))
        self.assertTrue(all("certificates" not in call[1] and "profiles" not in call[1] and "appGroups" not in call[1] for call in self.calls))
        return result, rendered

    def test_reuse_existing_identifiers_and_capabilities_without_writes(self):
        self.existing()
        original = copy.deepcopy(self.capabilities)
        result, rendered = self.invoke()
        self.assertEqual(result, 0)
        self.assertTrue(all(call[0] == "GET" for call in self.calls))
        self.assertEqual(self.capabilities, original)
        self.assertIn("Reused; exact identifier read-back verified", rendered)
        self.assertIn("association remain unverified and were not performed", rendered)

    def test_create_read_back_and_second_run_is_read_only(self):
        result, rendered = self.invoke()
        self.assertEqual(result, 0)
        self.assertEqual(len([call for call in self.calls if call[:2] == ("POST", "/bundleIds")]), 2)
        self.assertEqual(len([call for call in self.calls if call[:2] == ("POST", "/bundleIdCapabilities")]), 2)
        self.assertIn("Created; exact identifier read-back verified", rendered)
        self.calls.clear()
        result, _ = self.invoke()
        self.assertEqual(result, 0)
        self.assertTrue(all(call[0] == "GET" for call in self.calls))

    def test_add_only_app_groups_and_preserve_all_existing_capabilities(self):
        self.existing(groups=False)
        result, _ = self.invoke()
        self.assertEqual(result, 0)
        for capabilities in self.capabilities.values():
            self.assertEqual(capabilities, ["ASSOCIATED_DOMAINS", "PUSH_NOTIFICATIONS", "APP_GROUPS"])
        self.assertTrue(all(call[1] == "/bundleIdCapabilities" for call in self.calls if call[0] == "POST"))

    def test_get_authentication_failure_stops_before_writes(self):
        def rejected(method, path, query=None, body=None):
            self.calls.append((method, path, query, body))
            raise RuntimeError("HTTP 401 raw-private-error-body " + self.hidden)
        result, rendered = self.invoke(rejected)
        self.assertEqual(result, 1)
        self.assertIn("Authentication rejected (HTTP 401)", rendered)
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(self.calls[0][0], "GET")

    def test_uncertain_post_recovers_by_get_without_reposting(self):
        def uncertain(method, path, query=None, body=None):
            response = self.fake(method, path, query, body)
            if method == "POST":
                raise RuntimeError("raw-private-error-body " + self.hidden)
            return response
        result, rendered = self.invoke(uncertain)
        self.assertEqual(result, 0)
        self.assertIn("Present after uncertain create", rendered)
        self.assertEqual(len([call for call in self.calls if call[0] == "POST"]), 4)

    def test_uncertain_post_without_created_state_is_not_retried(self):
        def failed(method, path, query=None, body=None):
            if method == "POST":
                self.calls.append((method, path, query, body))
                raise RuntimeError("HTTP 403 raw-private-error-body " + self.hidden)
            return self.fake(method, path, query, body)
        result, rendered = self.invoke(failed)
        self.assertEqual(result, 1)
        self.assertIn("Write/read access denied (HTTP 403)", rendered)
        self.assertEqual(len([call for call in self.calls if call[0] == "POST"]), 2)
        for target in ensure.TARGETS:
            reads = [call for call in self.calls if call[0] == "GET" and call[2].get("filter[identifier]") == target[1]]
            self.assertEqual(len(reads), 2)

    def test_wrong_identifier_response_is_never_used_for_capability_writes(self):
        def wrong(method, path, query=None, body=None):
            if method == "GET" and path == "/bundleIds":
                self.calls.append((method, path, query, body))
                return {"data": [{"type": "bundleIds", "id": self.hidden,
                                  "attributes": {"identifier": "com.unrelated.blueberry", "platform": "IOS"}}]}
            return self.fake(method, path, query, body)
        result, rendered = self.invoke(wrong)
        self.assertEqual(result, 1)
        self.assertIn("Exact resource read-back failed", rendered)
        self.assertTrue(all(call[0] == "GET" and call[1] == "/bundleIds" for call in self.calls))

    def test_post_success_without_persistent_readback_is_failure(self):
        def lost(method, path, query=None, body=None):
            response = self.fake(method, path, query, body)
            if method == "POST" and path == "/bundleIds":
                self.bundles.clear()
            return response
        result, rendered = self.invoke(lost)
        self.assertEqual(result, 1)
        self.assertIn("Exact resource read-back failed", rendered)
        self.assertFalse(any(call[1] == "/bundleIdCapabilities" for call in self.calls))

    def test_malformed_post_response_recovers_only_through_verified_readback(self):
        def malformed(method, path, query=None, body=None):
            response = self.fake(method, path, query, body)
            return None if method == "POST" else response
        result, _ = self.invoke(malformed)
        self.assertEqual(result, 0)
        self.assertEqual(len([call for call in self.calls if call[0] == "POST"]), 4)

    def test_summary_and_annotations_do_not_contain_operational_values(self):
        self.existing()
        with tempfile.TemporaryDirectory() as directory:
            summary = Path(directory) / "summary.md"
            result, rendered = self.invoke(summary=summary)
            self.assertEqual(result, 0)
            self.assertIn("::notice title=Grill Master provisioning::", rendered)
            self.assertNotIn(str(summary), rendered)
            self.assertNotIn(self.hidden, summary.read_text())
            self.assertIn("App Store Connect app record", summary.read_text())

    def test_scope_guards_reject_unrelated_resource_before_api_call(self):
        report = ensure.Report()
        with self.assertRaises(ensure.ProvisionError), patch.object(ensure.inventory.asc, "request") as request:
            ensure.ensure_bundle("Unrelated", "com.unrelated.blueberry", "Blueberry", report)
        request.assert_not_called()
        with self.assertRaises(ensure.ProvisionError), patch.object(ensure.inventory.asc, "request") as request:
            ensure.post_once("/certificates", {})
        request.assert_not_called()


if __name__ == "__main__":
    unittest.main()
