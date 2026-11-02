"""Verify API key copy formats survive preparation without altering key material."""
import base64
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from apple_key import KeyInputError

SPEC = importlib.util.spec_from_file_location('prepare_signing_test', Path(__file__).with_name('prepare-signing.py'))
prepare = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(prepare)


class PreparedAPIKey(unittest.TestCase):
    def test_original_pem_and_wrapped_base64_preserve_a_valid_private_key(self):
        with tempfile.TemporaryDirectory() as root:
            original = Path(root) / 'original.p8'
            subprocess.run(['openssl', 'genpkey', '-algorithm', 'EC', '-pkeyopt', 'ec_paramgen_curve:P-256', '-out', str(original)], check=True, capture_output=True)
            key = original.read_bytes()
            for value in (key.decode('ascii'), base64.encodebytes(key).decode('ascii')):
                destination = Path(root) / 'prepared.p8'
                with patch.dict(os.environ, {'ASC_PRIVATE_KEY_P8_BASE64': value}):
                    prepare.decode_secret('ASC_PRIVATE_KEY_P8_BASE64', destination)
                self.assertEqual(destination.read_bytes().strip(), key.strip())
                self.assertEqual(destination.stat().st_mode & 0o777, 0o600)
                subprocess.run(['openssl', 'pkey', '-in', str(destination), '-check', '-noout'], check=True, capture_output=True)

    def test_command_input_is_rejected_without_writing_or_executing(self):
        with tempfile.TemporaryDirectory() as root:
            destination = Path(root) / 'prepared.p8'
            with patch.dict(os.environ, {'ASC_PRIVATE_KEY_P8_BASE64': 'base64 -i not-a-real-key | pbcopy'}):
                with self.assertRaises(KeyInputError) as caught:
                    prepare.decode_secret('ASC_PRIVATE_KEY_P8_BASE64', destination)
                self.assertEqual(caught.exception.kind, 'command_input')
            self.assertFalse(destination.exists())


if __name__ == '__main__':
    unittest.main()
