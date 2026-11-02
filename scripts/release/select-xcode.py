#!/usr/bin/env python3
"""Write DEVELOPER_DIR for the newest installed stable Xcode with an iOS SDK."""
import os
from pathlib import Path
import re
import subprocess


def main():
    candidates = set(path.resolve() for path in Path("/Applications").glob("Xcode*.app/Contents/Developer"))
    selected = subprocess.run(["xcode-select", "-p"], text=True, capture_output=True, check=True).stdout.strip()
    candidates.add(Path(selected).resolve())
    usable = []
    for candidate in candidates:
        environment = dict(os.environ, DEVELOPER_DIR=str(candidate))
        version = subprocess.run(["xcodebuild", "-version"], env=environment, text=True, capture_output=True)
        sdks = subprocess.run(["xcodebuild", "-showsdks"], env=environment, text=True, capture_output=True)
        match = re.search(r"^Xcode (\d+(?:\.\d+)*)", version.stdout, re.MULTILINE)
        if version.returncode == 0 and sdks.returncode == 0 and match and "-sdk iphoneos" in sdks.stdout:
            stable = "beta" not in str(candidate).lower()
            usable.append((stable, tuple(map(int, match[1].split("."))), str(candidate)))
    if not usable:
        raise SystemExit("No installed Xcode with an iOS device SDK found")
    print(f"DEVELOPER_DIR={max(usable)[2]}")


if __name__ == "__main__":
    main()
