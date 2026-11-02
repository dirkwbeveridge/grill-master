"""Offline contract tests: real ES256 signing plus mocked Apple metadata responses."""
import base64
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("asc", Path(__file__).with_name("app-store-connect.py"))
asc = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(asc)


class CryptoTests(unittest.TestCase):
    def test_jwt_signature_verifies_with_openssl(self):
        with tempfile.TemporaryDirectory() as directory:
            key = Path(directory) / "private.pem"
            public = Path(directory) / "public.pem"
            subprocess.run(["openssl", "ecparam", "-name", "prime256v1", "-genkey", "-noout", "-out", str(key)],
                           check=True, capture_output=True)
            subprocess.run(["openssl", "pkey", "-in", str(key), "-pubout", "-out", str(public)],
                           check=True, capture_output=True)
            with patch.dict(os.environ, {"ASC_KEY_ID": "test-key", "ASC_ISSUER_ID": "test-issuer", "ASC_KEY_PATH": str(key)}):
                token = asc.jwt()
            header, claims, signature = token.split(".")
            raw = base64.urlsafe_b64decode(signature + "==")
            self.assertEqual(len(raw), 64)
            self.assertEqual(json.loads(base64.urlsafe_b64decode(claims + "=="))["aud"], "appstoreconnect-v1")
            # Re-encode JWT's R || S to DER and check against the independent public key.
            components = []
            for value in (raw[:32], raw[32:]):
                value = value.lstrip(b"\0") or b"\0"
                if value[0] & 0x80:
                    value = b"\0" + value
                components.append(b"\x02" + bytes([len(value)]) + value)
            sequence = b"".join(components)
            signature_path = Path(directory) / "signature.der"
            signature_path.write_bytes(b"\x30" + bytes([len(sequence)]) + sequence)
            subprocess.run(["openssl", "dgst", "-sha256", "-verify", str(public), "-signature", str(signature_path)],
                           input=f"{header}.{claims}".encode(), check=True, capture_output=True)

    def test_malformed_der_rejected(self):
        for value in (b"", b"\x30\x05", b"\x30\x06\x02\x01\x01\x02\x01\x01extra"):
            with self.assertRaises(ValueError):
                asc.der_to_raw(value)


class MetadataTests(unittest.TestCase):
    def test_wait_for_visibility_create_and_read_back_notes(self):
        calls = []
        build_reads = 0
        written = False

        def fake(method, path, query=None, body=None):
            nonlocal build_reads, written
            calls.append((method, path, query, body))
            if path == "/apps":
                return {"data": [{"id": "app"}]}
            if path == "/builds":
                self.assertEqual(query["filter[version]"], "42")
                build_reads += 1
                return {"data": [] if build_reads == 1 else [{"id": "build", "attributes": {"processingState": "PROCESSING"}}]}
            if method == "POST":
                self.assertEqual(body["data"]["relationships"]["build"]["data"]["id"], "build")
                written = True
                return {}
            return {"data": [{"id": "notes", "attributes": {"locale": "en-US", "whatsNew": "Check timers"}}] if written else []}

        with patch.object(asc, "request", side_effect=fake), patch.object(asc.time, "sleep") as pause, \
                patch.dict(os.environ, {"TESTFLIGHT_WHATS_NEW": "Check timers"}):
            asc.verify_and_set_notes("42", attempts=2)
        pause.assert_called_once_with(15)
        self.assertEqual([c[0] for c in calls].count("POST"), 1)

    def test_existing_locale_is_updated_and_verified(self):
        responses = [{"data": [{"id": "app"}]},
                     {"data": [{"id": "build", "attributes": {"processingState": "VALID"}}]},
                     {"data": [{"id": "locale", "attributes": {"locale": "en-US", "whatsNew": "old"}}]},
                     {}, {"data": [{"id": "locale", "attributes": {"locale": "en-US", "whatsNew": "new"}}]}]
        with patch.object(asc, "request", side_effect=responses) as request, \
                patch.dict(os.environ, {"TESTFLIGHT_WHATS_NEW": "new"}):
            asc.verify_and_set_notes("42", attempts=1)
        self.assertEqual(request.call_args_list[3].args[:2], ("PATCH", "/betaBuildLocalizations/locale"))

    def test_invalid_build_never_writes_metadata(self):
        responses = [{"data": [{"id": "app"}]},
                     {"data": [{"id": "build", "attributes": {"processingState": "INVALID"}}]}]
        with patch.object(asc, "request", side_effect=responses) as request, \
                patch.dict(os.environ, {"TESTFLIGHT_WHATS_NEW": "notes"}):
            with self.assertRaisesRegex(RuntimeError, "INVALID"):
                asc.verify_and_set_notes("42", attempts=1)
        self.assertEqual(request.call_count, 2)

    def test_timeout_never_claims_upload_verified(self):
        responses = [{"data": [{"id": "app"}]}, {"data": []}]
        with patch.object(asc, "request", side_effect=responses), \
                patch.dict(os.environ, {"TESTFLIGHT_WHATS_NEW": "notes"}):
            with self.assertRaisesRegex(RuntimeError, "Upload not verified"):
                asc.verify_and_set_notes("42", attempts=1)

    def test_notes_readback_mismatch_fails(self):
        responses = [{"data": [{"id": "app"}]},
                     {"data": [{"id": "build", "attributes": {"processingState": "VALID"}}]},
                     {"data": []}, {}, {"data": []}]
        with patch.object(asc, "request", side_effect=responses), \
                patch.dict(os.environ, {"TESTFLIGHT_WHATS_NEW": "notes"}):
            with self.assertRaisesRegex(RuntimeError, "read-back verification"):
                asc.verify_and_set_notes("42", attempts=1)


if __name__ == "__main__":
    unittest.main()
