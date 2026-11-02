#!/usr/bin/env python3
"""Decode secret material outside checkout and validate distribution profiles."""
import base64
from datetime import datetime
import json
import os
from pathlib import Path
import plistlib
import subprocess
import sys

from apple_key import decode_private_key

BUNDLES = {"IOS_APP_PROFILE_BASE64": "com.dbeveridge.grillmaster",
           "IOS_WIDGET_PROFILE_BASE64": "com.dbeveridge.grillmaster.widgets"}
GROUP = "group.com.dbeveridge.grillmaster"


def decode_secret(name, path):
    value = os.environ[name]
    payload = decode_private_key(value) if name == "ASC_PRIVATE_KEY_P8_BASE64" else base64.b64decode(value, validate=True)
    path.write_bytes(payload)
    path.chmod(0o600)


def main():
    directory = Path(sys.argv[1])
    decode_secret("ASC_PRIVATE_KEY_P8_BASE64", directory / "AuthKey.p8")
    decode_secret("IOS_DISTRIBUTION_P12_BASE64", directory / "distribution.p12")
    installed = directory / "installed-profiles.txt"
    installed.write_text("")
    profiles = {}
    profile_dir = Path.home() / "Library/MobileDevice/Provisioning Profiles"
    profile_dir.mkdir(parents=True, exist_ok=True)
    for secret, bundle in BUNDLES.items():
        path = directory / f"{secret}.mobileprovision"
        decode_secret(secret, path)
        result = subprocess.run(["security", "cms", "-D", "-i", str(path)],
                                check=True, capture_output=True)
        profile = plistlib.loads(result.stdout)
        entitlements = profile["Entitlements"]
        team = os.environ["APPLE_TEAM_ID"]
        if team not in profile["TeamIdentifier"]:
            raise ValueError("Provisioning profile team mismatch")
        # AppIdentifierPrefix can differ from TeamIdentifier for legacy accounts.
        prefixes = profile.get("ApplicationIdentifierPrefix", [team])
        if entitlements.get("application-identifier") not in {f"{p}.{bundle}" for p in prefixes}:
            raise ValueError("Provisioning profile application identifier mismatch")
        if GROUP not in entitlements.get("com.apple.security.application-groups", []):
            raise ValueError("Provisioning profile missing shared App Group entitlement")
        if profile["ExpirationDate"] <= datetime.utcnow():
            raise ValueError("Provisioning profile expired")
        if profile.get("ProvisionedDevices") or profile.get("ProvisionsAllDevices") or entitlements.get("get-task-allow"):
            raise ValueError("Profile must be App Store distribution, not development/ad hoc/enterprise")
        uuid = profile["UUID"]
        if not all(c in "0123456789ABCDEFabcdef-" for c in uuid) or not uuid:
            raise ValueError("Invalid provisioning profile UUID")
        destination = profile_dir / f"{uuid}.mobileprovision"
        if not destination.exists():
            # Track before writing so cleanup also handles interrupted writes.
            with installed.open("a") as stream:
                stream.write(str(destination) + "\n")
            destination.write_bytes(path.read_bytes())
            destination.chmod(0o600)
        profiles[bundle] = uuid
    (directory / "profiles.json").write_text(json.dumps(profiles))
    options = {"method": "app-store-connect", "destination": "upload",
               "teamID": os.environ["APPLE_TEAM_ID"], "signingStyle": "manual",
               "signingCertificate": "Apple Distribution", "provisioningProfiles": profiles,
               "manageAppVersionAndBuildNumber": False, "testFlightInternalTestingOnly": False,
               "uploadSymbols": True, "stripSwiftSymbols": True}
    (directory / "ExportOptions.plist").write_bytes(plistlib.dumps(options))


if __name__ == "__main__":
    main()
