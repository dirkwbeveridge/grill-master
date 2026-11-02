#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
if [[ "$(uname -s)" != Darwin ]]; then
  echo 'Native validation requires macOS with Xcode.' >&2
  exit 1
fi
: "${RUNNER_TEMP:=${TMPDIR:-/tmp}}"
: "${IOS_DERIVED_DATA:=$RUNNER_TEMP/grillmaster-simulator-build}"
xcodebuild -version
xcodebuild -showsdks
echo '::notice title=Unsigned native validation::Starting simulator compilation.'
xcodebuild -workspace ios/App/App.xcworkspace -scheme App \
  -configuration Debug -sdk iphonesimulator -destination 'generic/platform=iOS Simulator' \
  -derivedDataPath "$IOS_DERIVED_DATA" CODE_SIGNING_ALLOWED=NO build
APP_PATH="$IOS_DERIVED_DATA/Build/Products/Debug-iphonesimulator/App.app"
test -d "$APP_PATH"
echo '::notice title=Unsigned native validation::Simulator compilation succeeded.'
if [[ "${CAPTURE_SCREENSHOTS:-1}" == 1 ]]; then
  export APP_PATH
  python3 scripts/release/capture-screenshots.py
fi
