#!/usr/bin/env python3
"""Verify an uploaded build and create/update its TestFlight What to Test notes.

Python standard library plus the system openssl executable; normal HTTPS trust.
No private key, JWT, operational identifiers, or API bodies are logged.
"""
import argparse
import base64
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.appstoreconnect.apple.com/v1"
BUNDLE = "com.dbeveridge.grillmaster"


def b64url(value):
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def der_to_raw(signature):
    """Convert OpenSSL ASN.1 ECDSA signature to JWT's fixed-width R || S."""
    cursor = 0

    def read(tag):
        nonlocal cursor
        if cursor + 2 > len(signature) or signature[cursor] != tag:
            raise ValueError("Invalid ECDSA signature encoding")
        cursor += 1
        length = signature[cursor]
        cursor += 1
        if length & 0x80:
            count = length & 0x7f
            if not count or cursor + count > len(signature):
                raise ValueError("Invalid ECDSA signature length")
            length = int.from_bytes(signature[cursor:cursor + count], "big")
            cursor += count
        end = cursor + length
        if end > len(signature):
            raise ValueError("Truncated ECDSA signature")
        return end

    sequence_end = read(0x30)
    values = []
    for _ in range(2):
        end = read(0x02)
        value = signature[cursor:end].lstrip(b"\0")
        if not value or len(value) > 32:
            raise ValueError("Invalid ES256 signature component")
        values.append(value.rjust(32, b"\0"))
        cursor = end
    if cursor != sequence_end or sequence_end != len(signature):
        raise ValueError("Invalid ECDSA signature trailing bytes")
    return b"".join(values)


def jwt():
    now = int(time.time())
    header = {"alg": "ES256", "kid": os.environ["ASC_KEY_ID"], "typ": "JWT"}
    claims = {"iss": os.environ["ASC_ISSUER_ID"], "iat": now - 5,
              "exp": now + 600, "aud": "appstoreconnect-v1"}
    unsigned = ".".join(b64url(json.dumps(item, separators=(",", ":")).encode())
                        for item in (header, claims))
    signed = subprocess.run(["openssl", "dgst", "-sha256", "-sign", os.environ["ASC_KEY_PATH"]],
                            input=unsigned.encode(), capture_output=True, check=True)
    return f"{unsigned}.{b64url(der_to_raw(signed.stdout))}"


def request(method, path, query=None, body=None):
    url = API + path
    if query:
        url += "?" + urllib.parse.urlencode(query)
    data = None if body is None else json.dumps(body).encode()
    for attempt in range(5):
        req = urllib.request.Request(url, data=data, method=method,
                                     headers={"Authorization": f"Bearer {jwt()}",
                                              "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                result = response.read()
                return json.loads(result) if result else {}
        except urllib.error.HTTPError as error:
            # Retrying POST after an uncertain server failure could duplicate metadata.
            if method == "GET" and (error.code == 429 or error.code >= 500) and attempt < 4:
                time.sleep(min(5 * 2 ** attempt, 60))
                continue
            raise RuntimeError(f"App Store Connect {method} request failed (HTTP {error.code}); no API body logged") from None
        except urllib.error.URLError:
            raise RuntimeError("App Store Connect HTTPS request failed; no credentials or response body logged") from None


def verify_and_set_notes(build_number, attempts=60, interval=15):
    notes = os.environ["TESTFLIGHT_WHATS_NEW"]
    if not notes.strip() or len(notes) > 4000:
        raise ValueError("What to Test must contain 1–4000 characters")
    apps = request("GET", "/apps", {"filter[bundleId]": BUNDLE, "limit": "2"})["data"]
    if len(apps) != 1:
        raise RuntimeError("Expected exactly one App Store Connect app for the configured bundle")
    app_id = apps[0]["id"]
    build = None
    for attempt in range(attempts):
        builds = request("GET", "/builds", {"filter[app]": app_id,
                         "filter[version]": build_number, "sort": "-uploadedDate", "limit": "2"})["data"]
        if len(builds) > 1:
            raise RuntimeError("Build number is ambiguous across marketing versions; use a globally increasing number")
        if builds:
            candidate = builds[0]
            state = candidate["attributes"]["processingState"]
            if state in {"PROCESSING", "VALID"}:
                build = candidate
                print(f"App Store Connect sees expected build {build_number}; processing state: {state}.")
                break
            if state in {"FAILED", "INVALID"}:
                raise RuntimeError(f"Apple build processing state is {state}")
        if attempt + 1 < attempts:
            time.sleep(interval)
    if build is None:
        raise RuntimeError("Upload not verified before timeout; check App Store Connect before retrying this build number")
    build_id = build["id"]
    localizations = request("GET", f"/builds/{build_id}/betaBuildLocalizations", {"limit": "200"})["data"]
    existing = next((item for item in localizations if item["attributes"]["locale"] == "en-US"), None)
    if existing:
        payload = {"data": {"type": "betaBuildLocalizations", "id": existing["id"],
                            "attributes": {"whatsNew": notes}}}
        request("PATCH", f"/betaBuildLocalizations/{existing['id']}", body=payload)
        action = "Updated"
    else:
        payload = {"data": {"type": "betaBuildLocalizations", "attributes": {"locale": "en-US", "whatsNew": notes},
                            "relationships": {"build": {"data": {"type": "builds", "id": build_id}}}}}
        request("POST", "/betaBuildLocalizations", body=payload)
        action = "Created"
    verified = request("GET", f"/builds/{build_id}/betaBuildLocalizations", {"limit": "200"})["data"]
    if not any(item["attributes"].get("locale") == "en-US"
               and item["attributes"].get("whatsNew") == notes for item in verified):
        raise RuntimeError("What to Test write did not match read-back verification")
    print(f"{action} What to Test; read-back verified (en-US).")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", required=True)
    args = parser.parse_args()
    try:
        verify_and_set_notes(args.build)
    except (RuntimeError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        # OpenSSL subprocess errors include the private-key path in repr; keep it private.
        message = "App Store Connect credentials or signing operation failed" if isinstance(error, (KeyError, subprocess.CalledProcessError)) else str(error)
        print(message, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
