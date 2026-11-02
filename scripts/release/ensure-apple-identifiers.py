#!/usr/bin/env python3
"""Idempotently create only Grill Master's two bundle IDs and APP_GROUPS capabilities.

Run without arguments using the same four secrets and RUNNER_TEMP as
check-apple-access.py. Optional GITHUB_STEP_SUMMARY receives a sanitized report.
Exit 0 means both identifiers/capabilities passed read-back; exit 1 means a check
failed or remains uncertain. No certificate, profile, or existing capability is
changed. The shared App Group itself and its associations are not managed.
"""
import importlib.util
import os
from pathlib import Path
import re

SPEC = importlib.util.spec_from_file_location("identifier_inventory", Path(__file__).with_name("check-apple-access.py"))
inventory = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(inventory)

TARGETS = (("Main app", "com.dbeveridge.grillmaster", "Grill Master"),
           ("Widget extension", "com.dbeveridge.grillmaster.widgets", "Grill Master Widgets"))


class ProvisionError(Exception):
    def __init__(self, kind):
        self.kind = kind


class Report:
    def __init__(self):
        self.rows = []
        self.failed = False

    def row(self, label, status, warning=False):
        self.rows.append((label, status, warning))

    def render(self):
        lines = ["## Grill Master identifier provisioning", "", "| Check | Status |", "| --- | --- |"]
        lines.extend(f"| {label} | {status} |" for label, status, _ in self.rows)
        lines += ["", "Only the main app and widget bundle identifiers and their App Groups capabilities are managed.",
                  "Exact shared App Group creation and association are unverified and were not performed.",
                  "Certificates, provisioning profiles, unrelated apps, and every existing capability remain untouched.",
                  "This does not create the App Store Connect app record or establish signed-build readiness.", ""]
        return "\n".join(lines)

    def emit(self):
        text = self.render()
        print(text)
        for label, status, warning in self.rows:
            level = "warning" if warning else "notice"
            print(f"::{level} title=Grill Master provisioning::{label}: {status}")
        print("::warning title=Grill Master provisioning::Exact shared App Group creation and association remain unverified and were not performed.")
        summary = os.environ.get("GITHUB_STEP_SUMMARY")
        if summary:
            try:
                with open(summary, "a", encoding="utf-8") as stream:
                    stream.write(text)
            except OSError:
                print("::warning title=Grill Master provisioning::Step summary could not be written; sanitized annotations remain available.")
                self.failed = True


def list_resources(path, query=None):
    try:
        return inventory.all_pages(path, query)[0]
    except inventory.InventoryError as error:
        raise ProvisionError(error.kind) from None
    except Exception:
        raise ProvisionError("request_failed") from None


def post_once(path, body):
    # The upload helper retries only GET requests; a POST is attempted exactly once.
    if path not in {"/bundleIds", "/bundleIdCapabilities"}:
        raise ProvisionError("scope_violation")
    try:
        return inventory.asc.request("POST", path, body=body)
    except Exception as error:
        match = re.search(r"\bHTTP (\d{3})\b", str(error))
        kind = {"401": "authentication_failed", "403": "permission_denied"}.get(match[1] if match else "", "request_failed")
        raise ProvisionError(kind) from None


def validate_bundle(resource, identifier):
    if not isinstance(resource, dict) or resource.get("type") != "bundleIds":
        raise ProvisionError("readback_failed")
    attributes = resource.get("attributes", {})
    resource_id = resource.get("id", "")
    if (attributes.get("identifier") != identifier or attributes.get("platform") not in {"IOS", "UNIVERSAL"}
            or not isinstance(resource_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", resource_id)):
        raise ProvisionError("readback_failed")
    return resource_id


def find_bundle(identifier):
    if identifier not in {target[1] for target in TARGETS}:
        raise ProvisionError("scope_violation")
    entries = list_resources("/bundleIds", {"filter[identifier]": identifier, "limit": "2",
                                           "fields[bundleIds]": "identifier,platform"})
    if not entries:
        return None
    if len(entries) != 1:
        raise ProvisionError("readback_failed")
    return validate_bundle(entries[0], identifier)


def ensure_bundle(label, identifier, name, report):
    if (label, identifier, name) not in TARGETS:
        raise ProvisionError("scope_violation")
    existing = find_bundle(identifier)
    if existing:
        report.row(f"{label} identifier", "Reused; exact identifier read-back verified")
        return existing
    body = {"data": {"type": "bundleIds", "attributes": {"name": name, "identifier": identifier, "platform": "IOS"}}}
    try:
        response = post_once("/bundleIds", body)
        if not isinstance(response, dict):
            raise ProvisionError("readback_failed")
        created = validate_bundle(response.get("data"), identifier)
    except ProvisionError as original:
        # The request might have reached Apple. One read-back can recover its result;
        # a second POST here could create a duplicate or obscure the original outcome.
        try:
            recovered = find_bundle(identifier)
        except ProvisionError:
            raise original
        if not recovered:
            raise original
        report.row(f"{label} identifier", "Present after uncertain create; exact identifier read-back verified")
        return recovered
    verified = find_bundle(identifier)
    if verified != created:
        raise ProvisionError("readback_failed")
    report.row(f"{label} identifier", "Created; exact identifier read-back verified")
    return verified


def has_app_groups(bundle_id):
    entries = list_resources(f"/bundleIds/{bundle_id}/bundleIdCapabilities", {"limit": "200"})
    matches = [entry for entry in entries if entry.get("attributes", {}).get("capabilityType") == "APP_GROUPS"]
    if len(matches) > 1:
        raise ProvisionError("readback_failed")
    return bool(matches)


def ensure_capability(label, bundle_id, report):
    if has_app_groups(bundle_id):
        report.row(f"{label} App Groups capability", "Reused; read-back verified")
        return
    body = {"data": {"type": "bundleIdCapabilities", "attributes": {"capabilityType": "APP_GROUPS", "settings": []},
                     "relationships": {"bundleId": {"data": {"type": "bundleIds", "id": bundle_id}}}}}
    try:
        response = post_once("/bundleIdCapabilities", body)
        if not isinstance(response, dict):
            raise ProvisionError("readback_failed")
        data = response.get("data", {})
        if not isinstance(data, dict) or data.get("type") != "bundleIdCapabilities" or data.get("attributes", {}).get("capabilityType") != "APP_GROUPS":
            raise ProvisionError("readback_failed")
    except ProvisionError as original:
        try:
            recovered = has_app_groups(bundle_id)
        except ProvisionError:
            raise original
        if not recovered:
            raise original
        report.row(f"{label} App Groups capability", "Present after uncertain create; read-back verified")
        return
    if not has_app_groups(bundle_id):
        raise ProvisionError("readback_failed")
    report.row(f"{label} App Groups capability", "Created; read-back verified")


def provision(report):
    statuses = {"authentication_failed": "Authentication rejected (HTTP 401); not verified",
                "permission_denied": "Write/read access denied (HTTP 403); not verified",
                "readback_failed": "Exact resource read-back failed; no further writes for this target",
                "scope_violation": "Scope validation failed; write blocked"}
    for label, identifier, name in TARGETS:
        try:
            bundle_id = ensure_bundle(label, identifier, name, report)
            ensure_capability(label, bundle_id, report)
        except ProvisionError as error:
            report.row(f"{label} provisioning", statuses.get(error.kind, "Request failed or outcome uncertain; rerun only after checking Apple state"), warning=True)
            report.failed = True
            if error.kind == "authentication_failed":
                break
        except Exception:
            report.row(f"{label} provisioning", "Failed safely; no diagnostic values disclosed", warning=True)
            report.failed = True


def main():
    report = Report()
    try:
        with inventory.credentials():
            report.row("Credential validation", "P-256 key and ES256 signing verified")
            provision(report)
    except Exception:
        report.row("Credential validation", "Failed; verify the configured secrets privately using the read-only inventory", warning=True)
        report.failed = True
    report.emit()
    return 1 if report.failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
