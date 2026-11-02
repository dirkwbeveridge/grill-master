#!/usr/bin/env python3
"""Capture the actual installed iOS app on fresh iPhone and iPad simulators."""
import json
import os
from pathlib import Path
import subprocess
import time


def run(*args, capture=False):
    return subprocess.run(args, check=True, text=True, capture_output=capture).stdout


def main():
    app = Path(os.environ["APP_PATH"]).resolve()
    output = Path(os.environ.get("SCREENSHOT_OUTPUT", "native-screenshots")).resolve()
    output.mkdir(parents=True, exist_ok=True)
    catalog = json.loads(run("xcrun", "simctl", "list", "--json", capture=True))
    runtimes = [r for r in catalog["runtimes"] if r.get("isAvailable")
                and r["identifier"].startswith("com.apple.CoreSimulator.SimRuntime.iOS-")]
    runtime = max(runtimes, key=lambda r: tuple(map(int, r["version"].split("."))))
    types = catalog["devicetypes"]
    preferred = {
        "iphone": ["iPhone 17 Pro Max", "iPhone 16 Pro Max", "iPhone 16", "iPhone 15 Pro Max"],
        "ipad": ["iPad Pro 13-inch (M5)", "iPad Pro 13-inch (M4)", "iPad Pro (12.9-inch) (6th generation)"],
    }
    evidence = {"runtime": runtime["name"], "captures": [],
                "limitations": ["Simulator captures; physical device validation remains required.",
                                "Active-cook screenshots require real UI automation and are not fabricated."]}
    for family, names in preferred.items():
        candidates = [t for n in names for t in types if t["name"] == n]
        candidates += [t for t in reversed(types) if t["name"].startswith("iPhone" if family == "iphone" else "iPad")
                       and t not in candidates]
        udid = None
        device = None
        # Some SDK catalogs include device types unsupported by an older installed runtime.
        for candidate in candidates:
            try:
                udid = run("xcrun", "simctl", "create", "Grill Master release capture",
                           candidate["identifier"], runtime["identifier"], capture=True).strip()
                device = candidate
                break
            except subprocess.CalledProcessError:
                continue
        if not udid:
            raise RuntimeError(f"No compatible {family} simulator")
        try:
            run("xcrun", "simctl", "boot", udid)
            run("xcrun", "simctl", "bootstatus", udid, "-b")
            run("xcrun", "simctl", "status_bar", udid, "override", "--time", "9:41",
                "--batteryState", "charged", "--batteryLevel", "100")
            run("xcrun", "simctl", "install", udid, str(app))
            run("xcrun", "simctl", "launch", udid, "com.dirkbeveridge.grillmaster")
            time.sleep(5)
            for state in ("configure", "temperatures"):
                route = f"grillmaster://{state}"
                run("xcrun", "simctl", "openurl", udid, route)
                time.sleep(3)
                filename = f"{family}-{state}.png"
                run("xcrun", "simctl", "io", udid, "screenshot", str(output / filename))
                evidence["captures"].append({"file": filename, "device": device["name"], "route": route})
        finally:
            subprocess.run(["xcrun", "simctl", "shutdown", udid], check=False)
            subprocess.run(["xcrun", "simctl", "delete", udid], check=False)
    (output / "capture-manifest.json").write_text(json.dumps(evidence, indent=2) + "\n")


if __name__ == "__main__":
    main()
