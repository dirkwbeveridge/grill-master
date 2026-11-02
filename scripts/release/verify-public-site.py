#!/usr/bin/env python3
"""Check the deployed public release documents from the deployment runner."""
import time
from urllib.request import Request, urlopen

BASE = "https://dirkwbeveridge.github.io/grill-master/"
EXPECTED = {
    "": ("Grill Master: Backyard Pro", "support/", "privacy/"),
    "support/": ("Support", "github.com/dirkwbeveridge/grill-master/issues"),
    "privacy/": ("Privacy", "Your cook records stay local."),
    "assets/site.css": ("font-family",),
}


def verify():
    for path, required in EXPECTED.items():
        request = Request(BASE + path, headers={"Cache-Control": "no-cache"})
        with urlopen(request, timeout=20) as response:
            if response.status != 200 or response.geturl() != BASE + path:
                raise ValueError("Unexpected public document status or redirect")
            content = response.read(1024 * 1024).decode("utf-8")
        if not all(text in content for text in required):
            raise ValueError("Public document content does not match the intended site")


if __name__ == "__main__":
    for attempt in range(12):
        try:
            verify()
            print("::notice::Public home, support, privacy, and stylesheet verified over HTTPS.")
            break
        except Exception:
            if attempt == 11:
                raise SystemExit("::error::Public site verification failed; deployment is not accepted.")
            time.sleep(10)
