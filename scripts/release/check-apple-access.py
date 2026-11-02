#!/usr/bin/env python3
"""Read-only Apple access/signing inventory; never creates account resources.

Run without arguments. Requires ASC_KEY_ID, ASC_ISSUER_ID,
ASC_PRIVATE_KEY_P8_BASE64, APPLE_TEAM_ID and RUNNER_TEMP (outside checkout).
Optional GITHUB_STEP_SUMMARY receives the same sanitized report as stdout.
Exit 0: queried prerequisites present; 1: credentials/access/request failure;
2: missing prerequisites or incomplete inventory. Read access never proves write access.
"""
import base64
from contextlib import contextmanager
from datetime import datetime, timezone
import importlib.util
import os
from pathlib import Path
import re
import subprocess
import tempfile
import urllib.parse

SPEC = importlib.util.spec_from_file_location("apple_inventory_asc", Path(__file__).with_name("app-store-connect.py"))
asc = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(asc)

BUNDLES = {"Main app": "com.dirkbeveridge.grillmaster", "Widget extension": "com.dirkbeveridge.grillmaster.widgets"}
DISTRIBUTION_TYPES = {"DISTRIBUTION", "IOS_DISTRIBUTION"}
P256_ALGORITHM = bytes.fromhex("06072a8648ce3d020106082a8648ce3d030107")
BINDING_FORMATS = {"ASC_KEY_ID": "exactly 10 uppercase ASCII letters or digits",
                   "ASC_ISSUER_ID": "a UUID with 8-4-4-4-12 hexadecimal digits",
                   "APPLE_TEAM_ID": "exactly 10 uppercase ASCII letters or digits"}
BINDING_LABELS = {"ASC_KEY_ID": "API key identifier",
                  "ASC_ISSUER_ID": "API issuer identifier",
                  "APPLE_TEAM_ID": "Apple developer membership identifier"}


class InventoryError(Exception):
    def __init__(self, kind, fields=()):
        self.kind = kind
        self.fields = fields


class Report:
    def __init__(self):
        self.rows = []
        self.missing = []
        self.access_failed = False

    def row(self, label, status):
        self.rows.append((label, status))

    def text(self):
        lines = ["## Apple signing access inventory", "", "Read-only inspection; no Apple account resources were changed.", "",
                 "| Check | Status |", "| --- | --- |"]
        lines.extend(f"| {label} | {status} |" for label, status in self.rows)
        lines += ["", "Missing prerequisites or checks:"]
        lines += [f"- {item}" for item in self.missing] if self.missing else ["- None found among the queried resources."]
        lines += ["", "Read permission does not prove permission to create certificates, identifiers, profiles, or uploads.",
                  "Team ID ownership and exact shared App Group membership are not established by these endpoints.",
                  "Visible certificates do not establish access to their private keys. Profile metadata does not prove signing compatibility.",
                  "Provisioning and a signed build remain separate verification steps.", ""]
        return "\n".join(lines)

    def code(self):
        return 1 if self.access_failed else (2 if self.missing else 0)

    def annotations(self):
        for label, status in self.rows:
            warning = status == "0" or any(word in status.lower() for word in ("missing", "failed", "invalid", "denied", "rejected", "unknown", "unverified", "ambiguous", "unavailable"))
            level = "warning" if warning else "notice"
            print(f"::{level} title=Apple signing inventory::{label}: {status}")
        for item in self.missing:
            print(f"::warning title=Apple signing prerequisite::{item}")


def tlv(data, offset=0):
    if offset + 2 > len(data):
        raise InventoryError("key_parse_failed")
    tag, length = data[offset:offset + 2]
    cursor = offset + 2
    if length & 0x80:
        count = length & 0x7f
        if not count or cursor + count > len(data):
            raise InventoryError("key_parse_failed")
        length = int.from_bytes(data[cursor:cursor + count], "big")
        cursor += count
    end = cursor + length
    if end > len(data):
        raise InventoryError("key_parse_failed")
    return tag, data[cursor:end], end


def validate_key(path):
    try:
        subprocess.run(["openssl", "pkey", "-in", str(path), "-check", "-noout"],
                       capture_output=True, check=True, timeout=15, input=b"")
        public = subprocess.run(["openssl", "pkey", "-in", str(path), "-pubout", "-outform", "DER"],
                                capture_output=True, check=True, timeout=15, input=b"").stdout
        tag, sequence, end = tlv(public)
        algorithm_tag, algorithm, _ = tlv(sequence)
        if tag != 0x30 or end != len(public) or algorithm_tag != 0x30:
            raise InventoryError("key_parse_failed")
        if algorithm != P256_ALGORITHM:
            raise InventoryError("wrong_curve")
    except (OSError, subprocess.SubprocessError, ValueError):
        raise InventoryError("key_parse_failed") from None


def decode_private_key(value):
    """Accept PEM or copy-wrapped Base64 as data; never interpret shell syntax."""
    text = value.strip(" \t\r\n")
    if re.match(r"(?:\$[ \t]*)?(?:/[^ \t\r\n]*/)?(?:base64|openssl|cat|echo|printf|pbpaste|gh)(?:[ \t\r\n]|$)", text):
        raise InventoryError("command_input")
    if text.startswith("-----BEGIN "):
        try:
            key = text.encode("ascii")
        except UnicodeEncodeError:
            raise InventoryError("key_parse_failed") from None
    else:
        compact = re.sub(r"[ \t\r\n]", "", text)
        try:
            key = base64.b64decode(compact, validate=True)
        except ValueError:
            raise InventoryError("invalid_base64") from None
    if key.startswith(b"-----BEGIN ENCRYPTED PRIVATE KEY-----"):
        raise InventoryError("key_parse_failed")
    if not key.startswith(b"-----BEGIN PRIVATE KEY-----"):
        raise InventoryError("missing_pem_header")
    return key


@contextmanager
def credentials():
    names = ("ASC_KEY_ID", "ASC_ISSUER_ID", "ASC_PRIVATE_KEY_P8_BASE64", "APPLE_TEAM_ID", "RUNNER_TEMP")
    if any(not os.environ.get(name) for name in names):
        raise InventoryError("missing_inputs")
    normalized = {name: os.environ[name].strip() for name in BINDING_FORMATS}
    invalid = []
    for name, value in normalized.items():
        if name == "ASC_ISSUER_ID":
            if not re.fullmatch(r"[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}", value):
                invalid.append(name)
        elif not re.fullmatch(r"[A-Z0-9]{10}", value):
            invalid.append(name)
    if invalid:
        raise InventoryError("malformed_bindings", fields=tuple(invalid))
    previous = {name: os.environ[name] for name in normalized}
    os.environ.update(normalized)
    try:
        with key_credentials():
            yield
    finally:
        os.environ.update(previous)


@contextmanager
def key_credentials():
    try:
        temporary_root = Path(os.environ["RUNNER_TEMP"]).resolve(strict=True)
        checkout = Path(__file__).resolve().parents[2]
        if temporary_root == checkout or checkout in temporary_root.parents or not temporary_root.is_dir():
            raise InventoryError("unsafe_temp")
    except InventoryError:
        raise
    except OSError:
        raise InventoryError("unsafe_temp") from None
    key = decode_private_key(os.environ["ASC_PRIVATE_KEY_P8_BASE64"])
    previous = os.environ.get("ASC_KEY_PATH")
    with tempfile.TemporaryDirectory(prefix="grillmaster-apple-inventory-", dir=temporary_root) as directory:
        path = Path(directory) / "AuthKey.p8"
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(key)
        validate_key(path)
        os.environ["ASC_KEY_PATH"] = str(path)
        try:
            # Ensures the existing upload helper can sign an ES256 JWT with this key.
            asc.jwt()
            yield
        finally:
            if previous is None:
                os.environ.pop("ASC_KEY_PATH", None)
            else:
                os.environ["ASC_KEY_PATH"] = previous


def get(path, query=None):
    try:
        return asc.request("GET", path, query=query)
    except Exception as error:
        # Never propagate exception text, URLs, response bodies, or operational IDs.
        match = re.search(r"\bHTTP (\d{3})\b", str(error))
        status = int(match[1]) if match else None
        kind = {401: "authentication_failed", 403: "permission_denied", 404: "unsupported", 405: "unsupported"}.get(status, "request_failed")
        raise InventoryError(kind) from None


def all_pages(path, query=None):
    data = []
    included = []
    for _ in range(100):
        response = get(path, query)
        if not isinstance(response.get("data"), list):
            raise InventoryError("request_failed")
        data.extend(response["data"])
        included.extend(response.get("included", []))
        next_url = response.get("links", {}).get("next")
        if not next_url:
            return data, included
        parsed = urllib.parse.urlsplit(next_url)
        if parsed.scheme != "https" or parsed.netloc != "api.appstoreconnect.apple.com" or not parsed.path.startswith("/v1/") or parsed.fragment:
            raise InventoryError("request_failed")
        path = parsed.path[len("/v1"):]
        query = dict(urllib.parse.parse_qsl(parsed.query, keep_blank_values=True))
    raise InventoryError("request_failed")


def unexpired(attributes):
    try:
        value = datetime.fromisoformat(attributes["expirationDate"].replace("Z", "+00:00"))
        return value.tzinfo is not None and value > datetime.now(timezone.utc)
    except (KeyError, TypeError, ValueError):
        return False


def failed_check(report, label, error, optional=False):
    statuses = {"authentication_failed": "Authentication rejected (HTTP 401)",
                "permission_denied": "Read access denied (HTTP 403)",
                "unsupported": "Endpoint unavailable", "request_failed": "Request failed; inventory unknown"}
    report.row(label, statuses.get(error.kind, "Check failed; inventory unknown"))
    report.missing.append(f"Resolve {label.lower()} access or verify the corresponding resources manually.")
    if error.kind != "unsupported" or not optional:
        report.access_failed = True


def inspect(report):
    # Auth failure is categorically different from an authenticated, empty resource list.
    try:
        apps, _ = all_pages("/apps", {"filter[bundleId]": BUNDLES["Main app"], "limit": "2",
                                       "fields[apps]": "bundleId"})
    except InventoryError as error:
        failed_check(report, "App Store Connect app", error)
        if error.kind == "authentication_failed":
            return
    else:
        exact = [app for app in apps if app.get("attributes", {}).get("bundleId") == BUNDLES["Main app"]]
        report.row("API authentication", "Accepted for app inventory read")
        report.row("App Store Connect app", "Present" if len(exact) == 1 else ("Missing" if not exact else "Ambiguous"))
        if len(exact) != 1:
            report.missing.append("Create or grant this key access to the main app's App Store Connect record.")
    bundle_ids = {}
    for label, identifier in BUNDLES.items():
        try:
            entries, _ = all_pages("/bundleIds", {"filter[identifier]": identifier, "limit": "2", "fields[bundleIds]": "identifier"})
            exact = [item for item in entries if item.get("attributes", {}).get("identifier") == identifier]
            report.row(f"{label} identifier", "Present" if len(exact) == 1 else ("Missing" if not exact else "Ambiguous"))
            if len(exact) != 1:
                report.missing.append(f"Register or verify the {label.lower()} identifier in this developer account.")
                continue
            bundle_id = exact[0]["id"]
            bundle_ids[label] = bundle_id
            capabilities, _ = all_pages(f"/bundleIds/{bundle_id}/bundleIdCapabilities", {"limit": "200"})
            enabled = any(item.get("attributes", {}).get("capabilityType") == "APP_GROUPS" for item in capabilities)
            report.row(f"{label} App Groups capability", "Enabled; group membership unverified" if enabled else "Missing")
            if not enabled:
                report.missing.append(f"Enable App Groups for the {label.lower()} identifier and associate the shared app group.")
        except InventoryError as error:
            failed_check(report, f"{label} identifier/capabilities", error)
            if error.kind == "authentication_failed":
                return
    try:
        certificates, _ = all_pages("/certificates", {"filter[certificateType]": "DISTRIBUTION,IOS_DISTRIBUTION", "limit": "200",
                                                      "fields[certificates]": "certificateType,expirationDate"})
        usable = sum(item.get("attributes", {}).get("certificateType") in DISTRIBUTION_TYPES
                     and unexpired(item["attributes"]) for item in certificates)
        report.row("Unexpired distribution certificates", str(usable))
        if not usable:
            report.missing.append("Create an Apple Distribution certificate backed by a securely owned private key; no unexpired distribution certificate is visible.")
    except InventoryError as error:
        failed_check(report, "Distribution certificate inventory", error)
        if error.kind == "authentication_failed":
            return
    try:
        profiles, _ = all_pages("/profiles", {"filter[profileType]": "IOS_APP_STORE", "limit": "200",
                                            "include": "bundleId,certificates",
                                            "fields[profiles]": "profileType,profileState,expirationDate,bundleId,certificates",
                                            "fields[bundleIds]": "identifier",
                                            "fields[certificates]": "certificateType,expirationDate"})
        for label in BUNDLES:
            count = sum(item.get("attributes", {}).get("profileType") == "IOS_APP_STORE"
                        and item["attributes"].get("profileState") == "ACTIVE" and unexpired(item["attributes"])
                        and item.get("relationships", {}).get("bundleId", {}).get("data", {}).get("id") == bundle_ids.get(label)
                        for item in profiles) if label in bundle_ids else 0
            report.row(f"{label} active App Store profiles", str(count))
            if not count:
                report.missing.append(f"Create or renew an App Store distribution profile for the {label.lower()} after capabilities and the signing certificate are configured.")
    except InventoryError as error:
        failed_check(report, "App Store profile inventory", error, optional=True)


def main():
    report = Report()
    try:
        with credentials():
            report.row("Local API key format", "Valid unencrypted PKCS#8 P-256 key; ES256 signing succeeded")
            inspect(report)
    except InventoryError as error:
        messages = {"missing_inputs": "Required credential inputs or RUNNER_TEMP are missing.",
                    "malformed_bindings": "Key ID, Issuer ID, or Team ID input format is invalid.",
                    "unsafe_temp": "RUNNER_TEMP must be an existing directory outside the checkout.",
                    "invalid_base64": "Private-key decoding failed: invalid Base64. Supply raw unencrypted PKCS#8 PEM or Base64 containing only the encoding and ASCII whitespace.",
                    "missing_pem_header": "Private-key decoding succeeded, but the input is missing the unencrypted PKCS#8 PEM header.",
                    "key_parse_failed": "Private-key validation failed: OpenSSL could not parse an unencrypted private key (malformed or encrypted input).",
                    "wrong_curve": "Private-key validation failed: the key is not EC P-256 required for ES256.",
                    "command_input": "Private-key input contains a pasted shell command instead of key data. Supply the command output or raw PEM; no command was executed."}
        report.row("Credential validation", "Failed")
        if error.kind == "malformed_bindings":
            for field in error.fields:
                expected = BINDING_FORMATS[field]
                report.row(f"{field} format", f"Invalid: expected {expected}")
                # A mistakenly stored placeholder can cause GitHub to mask the
                # field's name itself. A fixed descriptive label remains useful.
                report.row("Invalid input category", BINDING_LABELS[field])
                report.missing.append(f"Correct {field}: expected {expected}; surrounding whitespace is accepted.")
        else:
            report.missing.append(messages.get(error.kind, "Credential validation failed; verify the configured secrets privately."))
        report.access_failed = True
    except Exception:
        report.row("Inventory", "Failed safely; no diagnostic values disclosed")
        report.missing.append("Verify credential configuration, network access, and Apple API availability privately.")
        report.access_failed = True
    rendered = report.text()
    print(rendered)
    report.annotations()
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        try:
            with open(summary, "a", encoding="utf-8") as stream:
                stream.write(rendered)
        except OSError:
            print("GitHub step summary could not be written; inventory output above remains sanitized.")
            return 1
    return report.code()


if __name__ == "__main__":
    raise SystemExit(main())
