#!/usr/bin/env bash
# One automatic-signing attempt; no manual certificate/profile secrets required.
set -euo pipefail
set +x
umask 077
cd "$(dirname "$0")/../.."
if [[ "${1:-}" == --help ]]; then
  cat <<'HELP'
Usage: bash scripts/release/automatic-testflight.sh
Requires macOS/Xcode, synced CocoaPods workspace, RUNNER_TEMP outside checkout,
and ASC_KEY_ID, ASC_ISSUER_ID, ASC_PRIVATE_KEY_P8_BASE64, APPLE_TEAM_ID.
Optional BUILD_NUMBER defaults to 2. TESTFLIGHT_WHATS_NEW defaults to release
validation notes. The exact App Store Connect app must already exist, and the
build number must be unused. Automatic signing may create signing assets using
the authorized API key; no certificate is revoked or device registered here.
Archive/export/API verification run in one job with one private temporary
keychain; signing keys and logs are removed at exit. No project source changes.
HELP
  exit 0
fi
[[ $# == 0 ]] || { echo '::error title=Automatic TestFlight::No command-line arguments are supported.'; exit 1; }
[[ "$(uname -s)" == Darwin ]] || { echo '::error title=Automatic TestFlight::A Mac with Xcode is required.'; exit 1; }
[[ -n "${RUNNER_TEMP:-}" ]] || { echo '::error title=Automatic TestFlight::RUNNER_TEMP must point outside the checkout.'; exit 1; }
TEMP_RELEASE_DIR="$(mktemp -d "$RUNNER_TEMP/grillmaster-automatic.XXXXXX")"
TEMP_RELEASE_DIR="$(cd "$TEMP_RELEASE_DIR" && pwd -P)"
export TEMP_RELEASE_DIR
KEYCHAIN_PATH="$TEMP_RELEASE_DIR/signing.keychain-db"
KEYCHAIN_PASSWORD="$(openssl rand -hex 32)"
STATE_SAVED=0
KEYCHAIN_CREATED=0
KEYCHAIN_CHANGED=0
HELPER=scripts/release/prepare-automatic-release.py
cleanup() {
  local status=$?
  trap - EXIT
  set +e
  local cleanup_failed=0
  if [[ "$STATE_SAVED" == 1 && "$KEYCHAIN_CHANGED" == 1 ]]; then
    local original_keychains=()
    while IFS= read -r path; do original_keychains+=("$path"); done < "$TEMP_RELEASE_DIR/original-keychains.txt"
    local original_default
    original_default="$(cat "$TEMP_RELEASE_DIR/original-default.txt")"
    security default-keychain -d user -s "$original_default" >/dev/null 2>&1 || cleanup_failed=1
    security list-keychains -d user -s "${original_keychains[@]}" >/dev/null 2>&1 || cleanup_failed=1
  fi
  if [[ "$KEYCHAIN_CREATED" == 1 ]]; then
    security delete-keychain "$KEYCHAIN_PATH" >/dev/null 2>&1 || cleanup_failed=1
  fi
  python3 "$HELPER" cleanup-profiles "$TEMP_RELEASE_DIR" 2>/dev/null || cleanup_failed=1
  rm -rf "$TEMP_RELEASE_DIR" || cleanup_failed=1
  if [[ "$cleanup_failed" == 1 ]]; then
    echo '::warning title=Automatic TestFlight::Temporary signing cleanup or keychain restoration was incomplete; the runner must be disposed before reuse.'
    [[ "$status" != 0 ]] || status=1
  fi
  exit "$status"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

# This authenticated app/build preflight completes before any keychain or Xcode work.
python3 "$HELPER" prepare "$TEMP_RELEASE_DIR"
# Generated only by the trusted helper; all values are shell-quoted and file mode is 0600.
source "$TEMP_RELEASE_DIR/auth.env"
mkdir "$TEMP_RELEASE_DIR/tmp"
export TMPDIR="$TEMP_RELEASE_DIR/tmp/"
python3 "$HELPER" snapshot-profiles "$TEMP_RELEASE_DIR"

setup_keychain() {
  security list-keychains -d user | python3 -c 'import shlex,sys; print("\n".join(shlex.split(sys.stdin.read())))' > "$TEMP_RELEASE_DIR/original-keychains.txt" || return
  security default-keychain -d user | python3 -c 'import shlex,sys; values=shlex.split(sys.stdin.read()); assert len(values)==1; print(values[0])' > "$TEMP_RELEASE_DIR/original-default.txt" || return
  STATE_SAVED=1
  security create-keychain -p "$KEYCHAIN_PASSWORD" "$KEYCHAIN_PATH" || return
  KEYCHAIN_CREATED=1
  security set-keychain-settings -lut 21600 "$KEYCHAIN_PATH" || return
  security unlock-keychain -p "$KEYCHAIN_PASSWORD" "$KEYCHAIN_PATH" || return
  KEYCHAIN_CHANGED=1
  security default-keychain -d user -s "$KEYCHAIN_PATH" || return
  security list-keychains -d user -s "$KEYCHAIN_PATH" || return
}
if ! setup_keychain > "$TEMP_RELEASE_DIR/keychain.log" 2>&1; then
  python3 "$HELPER" diagnose "$TEMP_RELEASE_DIR/keychain.log" keychain
  exit 1
fi
xcodebuild -version
xcodebuild -showsdks
AUTH_ARGS=(-allowProvisioningUpdates -authenticationKeyPath "$ASC_KEY_PATH"
  -authenticationKeyID "$ASC_KEY_ID" -authenticationKeyIssuerID "$ASC_ISSUER_ID")
if ! xcodebuild -workspace ios/App/App.xcworkspace -scheme App -configuration Release \
    -destination 'generic/platform=iOS' -archivePath "$TEMP_RELEASE_DIR/App.xcarchive" \
    -derivedDataPath "$TEMP_RELEASE_DIR/DerivedData" "${AUTH_ARGS[@]}" \
    CODE_SIGN_STYLE=Automatic DEVELOPMENT_TEAM="$APPLE_TEAM_ID" \
    PROVISIONING_PROFILE_SPECIFIER= PROVISIONING_PROFILE= \
    CURRENT_PROJECT_VERSION="$BUILD_NUMBER" MARKETING_VERSION="$EXPECTED_MARKETING_VERSION" \
    archive > "$TEMP_RELEASE_DIR/archive.log" 2>&1; then
  python3 "$HELPER" diagnose "$TEMP_RELEASE_DIR/archive.log" archive
  exit 1
fi
if ! rg -q '\*\* ARCHIVE SUCCEEDED \*\*' "$TEMP_RELEASE_DIR/archive.log"; then
  python3 "$HELPER" diagnose "$TEMP_RELEASE_DIR/archive.log" archive
  exit 1
fi
python3 "$HELPER" verify-archive "$TEMP_RELEASE_DIR"
if ! xcodebuild -exportArchive -archivePath "$TEMP_RELEASE_DIR/App.xcarchive" \
    -exportPath "$TEMP_RELEASE_DIR/export" -exportOptionsPlist "$TEMP_RELEASE_DIR/ExportOptions.plist" \
    "${AUTH_ARGS[@]}" > "$TEMP_RELEASE_DIR/export.log" 2>&1; then
  python3 "$HELPER" diagnose "$TEMP_RELEASE_DIR/export.log" export
  exit 1
fi
if ! rg -q '\*\* EXPORT SUCCEEDED \*\*' "$TEMP_RELEASE_DIR/export.log" \
    || ! rg -qi 'Uploaded package is processing|Upload succeeded|UPLOAD SUCCEEDED' "$TEMP_RELEASE_DIR/export.log"; then
  python3 "$HELPER" diagnose "$TEMP_RELEASE_DIR/export.log" export
  exit 1
fi
echo '::notice title=Automatic TestFlight::Xcode reports successful archive and upload; independently checking Apple build visibility and What to Test.'
python3 scripts/release/app-store-connect.py --build "$BUILD_NUMBER"
