"""Decode Apple API key input as data without executing commands or logging values."""
import base64
import re


class KeyInputError(Exception):
    def __init__(self, kind):
        self.kind = kind
        super().__init__(kind)


def decode_private_key(value):
    """Accept PEM or copy-wrapped Base64 as data; never interpret shell syntax."""
    text = value.strip(" \t\r\n")
    if re.match(r"(?:\$[ \t]*)?(?:/[^ \t\r\n]*/)?(?:base64|openssl|cat|echo|printf|pbpaste|gh)(?:[ \t\r\n]|$)", text):
        raise KeyInputError("command_input")
    if text.startswith("-----BEGIN "):
        try:
            key = text.encode("ascii")
        except UnicodeEncodeError:
            raise KeyInputError("key_parse_failed") from None
    else:
        compact = re.sub(r"[ \t\r\n]", "", text)
        try:
            key = base64.b64decode(compact, validate=True)
        except ValueError:
            raise KeyInputError("invalid_base64") from None
    if key.startswith(b"-----BEGIN ENCRYPTED PRIVATE KEY-----"):
        raise KeyInputError("key_parse_failed")
    if not key.startswith(b"-----BEGIN PRIVATE KEY-----"):
        raise KeyInputError("missing_pem_header")
    return key

