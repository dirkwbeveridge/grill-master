#!/usr/bin/env python3
"""Read only the exact owner-supplied App Store app; never print credentials/bodies."""
import importlib.util
import re
import base64
import os
import subprocess
from pathlib import Path

spec = importlib.util.spec_from_file_location("app_inventory", Path(__file__).with_name("check-apple-access.py"))
inventory = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inventory)

if __name__ == "__main__":
    try:
        with inventory.credentials():
            certificates, _ = inventory.all_pages("/certificates", {
                "filter[certificateType]": "DISTRIBUTION,IOS_DISTRIBUTION", "limit": "200",
                "fields[certificates]": "certificateContent,expirationDate"})
            teams = set()
            for certificate in certificates:
                value = certificate.get("attributes", {}).get("certificateContent", "")
                try:
                    data = base64.b64decode(value, validate=True)
                except (ValueError, TypeError):
                    continue
                parsed = subprocess.run(["openssl", "x509", "-inform", "DER", "-noout", "-subject", "-nameopt", "RFC2253"],
                                        input=data, capture_output=True)
                if parsed.returncode == 0:
                    match = re.search(rb"(?:^|,)OU=([A-Z0-9]{10})(?:,|$)", parsed.stdout)
                    if match: teams.add(match.group(1).decode("ascii"))
            if teams and os.environ["APPLE_TEAM_ID"].strip() not in teams:
                raise SystemExit("::error title=Apple signing team::Configured APPLE_TEAM_ID does not match the team in accessible distribution certificates. Correct that secret before retrying signing; no certificate was changed.")
            if teams:
                print("::notice title=Apple signing team::Configured Team ID matches an accessible distribution certificate.")
            else:
                print("::warning title=Apple signing team::Certificate data did not establish the configured Team ID; verify it privately.")
            response = inventory.get("/apps/6829659639", {"fields[apps]": "bundleId,name"})
        app = response.get("data", {})
        if app.get("id") != "6829659639":
            raise inventory.InventoryError("request_failed")
        attributes = app.get("attributes", {})
        bundle = attributes.get("bundleId", "")
        if not isinstance(bundle, str) or not re.fullmatch(r"[A-Za-z0-9.-]{1,255}", bundle):
            raise inventory.InventoryError("request_failed")
        print("::notice title=Exact Apple app record::Registered Bundle ID: " + bundle)
        print("::notice title=Exact Apple app record::Approved listing name matches: " + str(attributes.get("name") == "Grill Master: Backyard Pro"))
        if bundle != "com.dbeveridge.grillmaster":
            raise SystemExit("::error title=Exact Apple app record::Record is accessible, but its Bundle ID differs from the owner-supplied value. Do not provision or upload until reconciled.")
        print("::notice title=Exact Apple app record::Owner-supplied Apple ID is accessible and its Bundle ID matches.")
        if attributes.get("name") != "Grill Master: Backyard Pro":
            print("::warning title=Exact Apple app record::The app name differs from the approved listing title; review the listing before submission.")
    except inventory.InventoryError as error:
        messages = {
            "unsupported": "Owner-supplied Apple ID is not found or not visible to the configured API key. Check App Store Connect team/provider and key access; no account resources were changed.",
            "permission_denied": "Configured API key is denied access to the owner-supplied Apple ID. Check key role and app access.",
            "authentication_failed": "Apple rejected API authentication while reading the owner-supplied Apple ID.",
        }
        raise SystemExit("::error title=Exact Apple app record::" + messages.get(error.kind, "Exact app-record lookup failed safely; no account resources were changed."))
