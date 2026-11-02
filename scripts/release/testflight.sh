#!/usr/bin/env bash
# Usage and signing prerequisites: scripts/release/README.md
set -euo pipefail
set +x
umask 077
cd "$(dirname "$0")/../.."
if [[ "${1:-}" == --help ]]; then
  cat scripts/release/README.md
  exit 0
fi
[[ "$(uname -s)" == Darwin ]] || { echo 'TestFlight requires macOS with Xcode.' >&2; exit 1; }
for variable in BUILD_NUMBER TESTFLIGHT_WHATS_NEW ASC_KEY_ID ASC_ISSUER_ID ASC_PRIVATE_KEY_P8_BASE64 \
    APPLE_TEAM_ID IOS_DISTRIBUTION_P12_BASE64 IOS_DISTRIBUTION_P12_PASSWORD \
    IOS_APP_PROFILE_BASE64 IOS_WIDGET_PROFILE_BASE64; do
  [[ -n "${!variable:-}" ]] || { echo "Required environment variable missing: $variable" >&2; exit 1; }
done
[[ "$BUILD_NUMBER" =~ ^[1-9][0-9]*$ ]] || { echo 'BUILD_NUMBER must be a positive integer.' >&2; exit 1; }
[[ ${#TESTFLIGHT_WHATS_NEW} -le 4000 ]] || { echo 'What to Test must be at most 4000 characters.' >&2; exit 1; }
TEMP_RELEASE_DIR="$(mktemp -d "${RUNNER_TEMP:-${TMPDIR:-/tmp}}/grillmaster-release.XXXXXX")"
TEMP_RELEASE_DIR="$(cd "$TEMP_RELEASE_DIR" && pwd -P)"
if [[ "$TEMP_RELEASE_DIR" == "$(pwd -P)"/* ]]; then
  rmdir "$TEMP_RELEASE_DIR"
  echo 'Release temporary directory must be outside the repository.' >&2
  exit 1
fi
export TEMP_RELEASE_DIR
mkdir "$TEMP_RELEASE_DIR/tmp"
export TMPDIR="$TEMP_RELEASE_DIR/tmp/"
KEYCHAIN_PATH="$TEMP_RELEASE_DIR/signing.keychain-db"
KEYCHAIN_PASSWORD="$(openssl rand -hex 32)"
PROJECT_FILE=ios/App/App.xcodeproj/project.pbxproj
cp "$PROJECT_FILE" "$TEMP_RELEASE_DIR/project.pbxproj.original"
security list-keychains -d user | python3 -c 'import shlex,sys; print("\n".join(shlex.split(sys.stdin.read())))' > "$TEMP_RELEASE_DIR/original-keychains.txt"
cleanup() {
  local status=$?
  trap - EXIT
  cp "$TEMP_RELEASE_DIR/project.pbxproj.original" "$PROJECT_FILE" || true
  local original_keychains=()
  while IFS= read -r path; do original_keychains+=("$path"); done < "$TEMP_RELEASE_DIR/original-keychains.txt"
  security list-keychains -d user -s "${original_keychains[@]}" >/dev/null 2>&1 || true
  security delete-keychain "$KEYCHAIN_PATH" >/dev/null 2>&1 || true
  if [[ -f "$TEMP_RELEASE_DIR/installed-profiles.txt" ]]; then
    while IFS= read -r path; do rm -f "$path"; done < "$TEMP_RELEASE_DIR/installed-profiles.txt"
  fi
  rm -rf "$TEMP_RELEASE_DIR"
  exit "$status"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
python3 scripts/release/prepare-signing.py "$TEMP_RELEASE_DIR"
export ASC_KEY_PATH="$TEMP_RELEASE_DIR/AuthKey.p8"
security create-keychain -p "$KEYCHAIN_PASSWORD" "$KEYCHAIN_PATH" >/dev/null 2>&1
security set-keychain-settings -lut 21600 "$KEYCHAIN_PATH"
security unlock-keychain -p "$KEYCHAIN_PASSWORD" "$KEYCHAIN_PATH"
security import "$TEMP_RELEASE_DIR/distribution.p12" -P "$IOS_DISTRIBUTION_P12_PASSWORD" \
  -T /usr/bin/codesign -T /usr/bin/security -t cert -f pkcs12 -k "$KEYCHAIN_PATH" >/dev/null 2>&1
security set-key-partition-list -S apple-tool:,apple:,codesign: -s -k "$KEYCHAIN_PASSWORD" "$KEYCHAIN_PATH" >/dev/null 2>&1
original_keychains=()
while IFS= read -r path; do original_keychains+=("$path"); done < "$TEMP_RELEASE_DIR/original-keychains.txt"
security list-keychains -d user -s "$KEYCHAIN_PATH" "${original_keychains[@]}"
ruby scripts/release/configure-signing.rb "$TEMP_RELEASE_DIR/profiles.json"
xcodebuild -version
xcodebuild -showsdks
if ! xcodebuild -workspace ios/App/App.xcworkspace -scheme App -configuration Release \
    -destination 'generic/platform=iOS' -archivePath "$TEMP_RELEASE_DIR/App.xcarchive" \
    -derivedDataPath "$TEMP_RELEASE_DIR/DerivedData" CURRENT_PROJECT_VERSION="$BUILD_NUMBER" \
    archive > "$TEMP_RELEASE_DIR/archive.log" 2>&1; then
  echo 'Archive failed. Check Xcode project, certificate, App Group, and distribution profiles; private logs were not published.' >&2
  exit 1
fi
rg -q '\*\* ARCHIVE SUCCEEDED \*\*' "$TEMP_RELEASE_DIR/archive.log"
python3 - "$TEMP_RELEASE_DIR/App.xcarchive" "$BUILD_NUMBER" <<'PY'
from pathlib import Path
import plistlib
import sys
archive = Path(sys.argv[1])
app = next((archive / 'Products/Applications').glob('*.app'))
info = plistlib.loads((app / 'Info.plist').read_bytes())
assert info.get('ITSAppUsesNonExemptEncryption') is False, 'Archive encryption compliance key must be false'
assert info['CFBundleVersion'] == sys.argv[2], 'Archive build number mismatch'
extensions = list((app / 'PlugIns').glob('*.appex'))
assert extensions, 'Widget/Live Activity extension missing from archive'
for extension in extensions:
    extension_info = plistlib.loads((extension / 'Info.plist').read_bytes())
    assert extension_info['CFBundleVersion'] == sys.argv[2], 'Extension build number mismatch'
print('Archive succeeded; embedded extension and build number verified.')
PY
if ! xcodebuild -exportArchive -archivePath "$TEMP_RELEASE_DIR/App.xcarchive" \
    -exportPath "$TEMP_RELEASE_DIR/export" -exportOptionsPlist "$TEMP_RELEASE_DIR/ExportOptions.plist" \
    -authenticationKeyPath "$ASC_KEY_PATH" -authenticationKeyID "$ASC_KEY_ID" \
    -authenticationKeyIssuerID "$ASC_ISSUER_ID" > "$TEMP_RELEASE_DIR/export.log" 2>&1; then
  echo 'Export/upload failed. Check signing, App Store Connect key access, and build number. No distribution logs were published.' >&2
  exit 1
fi
rg -q '\*\* EXPORT SUCCEEDED \*\*' "$TEMP_RELEASE_DIR/export.log"
rg -qi 'Uploaded package is processing|Upload succeeded|Upload Succeeded|UPLOAD SUCCEEDED' "$TEMP_RELEASE_DIR/export.log"
echo 'Xcode reports archive and upload succeeded. Verifying App Store Connect.'
python3 scripts/release/app-store-connect.py --build "$BUILD_NUMBER"
