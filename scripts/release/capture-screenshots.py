#!/usr/bin/env python3
"""Capture the actual installed iOS app on fresh iPhone and iPad simulators."""
import json
import os
from pathlib import Path
import subprocess
import time
import tempfile

BUNDLE_ID = "com.dirkbeveridge.grillmaster"
CAPTURE_METHOD = "debug launch argument; real native app"
READY_RELATIVE_PATH = Path("Library/Caches/GrillMaster/debug-route-ready.json")


def run(*args, capture=False):
    return subprocess.run(args, check=True, text=True, capture_output=capture).stdout


def launch_state(udid, state, timeout=20):
    """Wait for the real web bridge to consume the Debug-only native route."""
    container = Path(run("xcrun", "simctl", "get_app_container", udid,
                         BUNDLE_ID, "data", capture=True).strip())
    marker = container / READY_RELATIVE_PATH
    subprocess.run(["xcrun", "simctl", "terminate", udid, BUNDLE_ID],
                   check=False, capture_output=True, text=True)
    # Remove previous-process evidence before launch; a fresh marker is mandatory.
    marker.unlink(missing_ok=True)
    arguments = ["--grill-route", state]
    run("xcrun", "simctl", "launch", udid, BUNDLE_ID, *arguments)
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            readiness = json.loads(marker.read_text())
        except (FileNotFoundError, json.JSONDecodeError):
            readiness = {}
        if (readiness.get("destination") == state
                and readiness.get("readiness") == "native route consumed by web bridge"):
            # Consumption proves the handoff, not completed rendering or visible labels.
            time.sleep(2)
            return {"destination": state, "launchArguments": arguments,
                    "readiness": "native route consumed by web bridge; 2s render wait"}
        time.sleep(0.2)
    raise RuntimeError(f"Debug route {state!r} was not consumed within {timeout}s")


def capture_visible_content(udid, destination, checker, timeout=60):
    """Retry actual simulator captures while the system still shows a blank launch view."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        run("xcrun", "simctl", "io", udid, "screenshot", str(destination))
        result = subprocess.run([str(checker), str(destination)], check=False)
        if result.returncode == 0:
            return
        if result.returncode != 1:
            raise RuntimeError("Unable to inspect native screenshot content")
        destination.unlink(missing_ok=True)
        time.sleep(2)
    raise RuntimeError("Native screenshot remained blank; refusing to publish it")


def main():
    app = Path(os.environ["APP_PATH"]).resolve()
    output = Path(os.environ.get("SCREENSHOT_OUTPUT", "native-screenshots")).resolve()
    output.mkdir(parents=True, exist_ok=True)
    # Compile once on the macOS runner; no third-party image dependency is needed.
    temporary = tempfile.TemporaryDirectory(prefix="grill-capture-")
    checker = Path(temporary.name) / "check-capture-content"
    run("xcrun", "swiftc", str(Path(__file__).with_name("check-capture-content.swift")),
        "-o", str(checker))
    catalog = json.loads(run("xcrun", "simctl", "list", "--json", capture=True))
    runtimes = [r for r in catalog["runtimes"] if r.get("isAvailable")
                and r["identifier"].startswith("com.apple.CoreSimulator.SimRuntime.iOS-")]
    runtime = max(runtimes, key=lambda r: tuple(map(int, r["version"].split("."))))
    types = catalog["devicetypes"]
    preferred = {
        "iphone": ["iPhone 17 Pro Max", "iPhone 16 Pro Max", "iPhone 16", "iPhone 15 Pro Max"],
        "ipad": ["iPad Pro 13-inch (M5)", "iPad Pro 13-inch (M4)", "iPad Pro (12.9-inch) (6th generation)"],
    }
    evidence = {"runtime": runtime["name"], "captureMethod": CAPTURE_METHOD, "captures": [],
                "limitations": ["Simulator captures; physical device validation remains required.",
                                "Debug launch routing does not validate open-URL prompts, Siri, or Shortcuts.",
                                "Bridge consumption and render wait require visual screen-label verification.",
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
            for state in ("configure", "temperatures"):
                readiness = launch_state(udid, state)
                filename = f"{family}-{state}.png"
                capture_visible_content(udid, output / filename, checker)
                evidence["captures"].append({"file": filename, "device": device["name"], **readiness})
        finally:
            subprocess.run(["xcrun", "simctl", "shutdown", udid], check=False)
            subprocess.run(["xcrun", "simctl", "delete", udid], check=False)
    (output / "capture-manifest.json").write_text(json.dumps(evidence, indent=2) + "\n")


if __name__ == "__main__":
    main()
