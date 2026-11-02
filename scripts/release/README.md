# Native validation and TestFlight release

These scripts require macOS, Xcode with an installed iOS runtime, Node 20 or newer (automatic release uses Node 24), Python 3, OpenSSL, and CocoaPods (including its `xcodeproj` Ruby gem). CI dynamically selects the newest installed stable Xcode with an iOS device SDK (a beta is used only if no stable installation qualifies); local scripts use your active Xcode. Both build paths record `xcodebuild -version` and installed SDKs. The workflow's `macos-15` runner label does **not** establish compliance with Apple's current SDK upload requirements; check the recorded Xcode/SDK against App Store Connect's requirements before a release.

Unsigned macOS validation succeeded for commit cb52b374bd21963bf390f5917cfa2cb2520bb0cc in GitHub run 41384119053, producing an iPhone/iPad screenshot artifact. Those captures still require visual acceptance. Apple API authentication has since succeeded with the four configured secrets. Signed archive/upload is pending the automatic release result. Physical-device testing remains a release gate.

## Automatic signing with the four existing secrets

The preferred `Automatic TestFlight release` workflow uses only `ASC_KEY_ID`,
`ASC_ISSUER_ID`, `ASC_PRIVATE_KEY_P8_BASE64`, and `APPLE_TEAM_ID` from the
`testflight` GitHub environment. Raw original `.p8` text and Base64 are both accepted;
the secret's legacy name does not require Base64.

The exact App Store Connect app must exist for `com.dbeveridge.grillmaster`.
Both it and `com.dbeveridge.grillmaster.widgets` must have the shared group
`group.com.dbeveridge.grillmaster` associated. The owner reports these portal
steps complete; API visibility and signed entitlements must independently confirm them.

Unsigned simulator compilation runs first. Store screenshots run in the separate
`iOS native validation` workflow and still require visual acceptance before an App
Store submission; they are not required for an internal TestFlight upload. The release job then checks the app record
and unused build number before creating a temporary keychain or requesting signing.
Xcode attempts automatic signing once using the API key. Existing certificate
metadata does not supply its private key, so four secrets are not a guarantee of
successful signing. Diagnose any failure before another provisioning attempt;
never revoke certificates belonging to Blueberry or register devices as a workaround.

The signed archive must contain the correct app and widget, matching versions/builds,
valid signatures, unexpired embedded profiles, and the intended team and App Group.
Only then does Xcode upload. Apple build visibility and a read-back of What to Test
establish completion. No external group, Beta App Review, or public App Store release
is submitted automatically. Signing material and raw distribution logs are never
published and are removed from the ephemeral runner at exit.

## Manual signing fallback (only if automatic signing requires it)

1. Create/register the App Store Connect app for `com.dbeveridge.grillmaster` and extension identifier `com.dbeveridge.grillmaster.widgets` in the same Apple Developer team. Enable the shared App Group `group.com.dbeveridge.grillmaster` on both identifiers; generate fresh profiles after capability changes.
2. Generate two **App Store distribution** provisioning profiles, one per identifier. Development, ad hoc, and enterprise profiles are rejected. Both profiles must include the shared App Group and match the distribution certificate and team.
3. Export the Apple Distribution certificate **with its private key** as a password-protected `.p12`. This is separate from the App Store Connect API `.p8` key.
4. Create an App Store Connect API key authorized to upload builds and manage TestFlight metadata for this app (App Manager access is appropriate). Keep the `.p8` outside the checkout and outside synced folders. Record its Key ID and Issuer ID privately. Do not paste these into issues or workflow inputs.
5. Create a GitHub Actions environment named `testflight`. Configure any desired release-branch restrictions/reviewers there. Reuse existing matching bindings if already configured; otherwise add these environment secrets using GitHub's encrypted secrets UI, or `gh secret set NAME --env testflight` with stdin from a protected local file; do not put secret values on the command line or commit them:

| Secret | Value |
| --- | --- |
| `ASC_KEY_ID` | App Store Connect API Key ID |
| `ASC_ISSUER_ID` | App Store Connect API Issuer ID |
| `ASC_PRIVATE_KEY_P8_BASE64` | Full original API `.p8` text, including BEGIN/END lines, or Base64-encoded file contents |
| `APPLE_TEAM_ID` | Apple Developer Team ID |
| `IOS_DISTRIBUTION_P12_BASE64` | Single-line base64 of the distribution certificate/private-key `.p12` |
| `IOS_DISTRIBUTION_P12_PASSWORD` | Password used when exporting that `.p12` |
| `IOS_APP_PROFILE_BASE64` | Single-line base64 of the main app's `.mobileprovision` |
| `IOS_WIDGET_PROFILE_BASE64` | Single-line base64 of the widget extension's `.mobileprovision` |

For the API key, you can open the downloaded `.p8` file as text, copy its entire contents including the BEGIN/END lines, and paste directly into the GitHub secret named `ASC_PRIVATE_KEY_P8_BASE64`. That existing secret name is retained for compatibility; raw PEM and Base64 are both supported. Paste file data, never a shell command.

For example, from macOS, `base64 -i /private/path/AuthKey.p8 | tr -d '\n' | gh secret set ASC_PRIVATE_KEY_P8_BASE64 --env testflight` sends the encoded key through stdin without printing it. Run from the correct repository. Use the same pattern for profiles and the `.p12`; delete temporary secret files securely according to your normal key-management process. Base64 is encoding, not encryption.

## Unsigned simulator validation

```bash
npm ci
npx cap sync ios
bash scripts/release/validate-ios.sh
```

The `iOS native validation` workflow runs on PRs, main pushes, and manual dispatch. It builds `App` from `ios/App/App.xcworkspace` with signing disabled, installs the actual compiled `.app` on fresh iPhone and iPad simulators, and captures the configuration and temperature-guide destinations through the real native bridge using Debug-only launch arguments (`--grill-route`). Release builds exclude that capture hook. The script waits for a fresh bridge-consumption marker and visible screenshot content, rejecting blank launch screens; visual acceptance still remains mandatory. It chooses an available iOS runtime/device and records the exact runtime, devices, and routes in `native-screenshots/capture-manifest.json`. PNGs and the manifest are retained for 14 days. Check these images for route correctness and layout; a screenshot file existing alone does not prove the screen's semantics.

These are native app simulator screenshots, not browser artwork. No cooking state is fabricated. Active-cook/Live Activity screenshots, notification behavior, widget interaction, and real-device checks remain pending genuine UI automation or physical device validation. To only compile locally, set `CAPTURE_SCREENSHOTS=0`. Set `SCREENSHOT_OUTPUT` to move captures outside the checkout.

## Manual TestFlight release

Dispatch **TestFlight release** from the intended commit/branch. Supply a new positive integer `build_number` greater than previously uploaded builds, and the `whats_new` text. The validation job must succeed before the upload job starts. Both jobs check out the same workflow commit.

The upload script (`bash scripts/release/testflight.sh --help` shows this guide):

- Imports the certificate into a temporary keychain and validates/installs the app and widget profiles, using separate profile UUIDs per target.
- Applies manual signing temporarily and archives a generic iOS device Release build. `CURRENT_PROJECT_VERSION` overrides **both** main app and extension; no source version bump is committed.
- Checks the actual archive includes the extension, matching build numbers, and `ITSAppUsesNonExemptEncryption=false`. That declaration is appropriate only while the app's encryption usage remains exempt; reassess it if encryption features change.
- Uses `xcodebuild -exportArchive` with `destination=upload`, App Store Connect API authentication, manual distribution signing, and version auto-management disabled. The export allows later external testing; it does not submit Beta App Review or assign an external group.
- Requires Xcode archive/export success markers and an upload-success marker, then independently polls App Store Connect for this exact build number. `PROCESSING` and `VALID` are accepted visibility states; `PROCESSING` does not mean processing or review has completed.
- Creates/updates the English (US) TestFlight **What to Test** notes and reads them back to verify. An eventual-consistency/API timeout fails the workflow even if the upload reached Apple; check App Store Connect before retrying the same build number.
- Restores the project signing settings and keychain search list and removes temporary keys, certificate, installed profiles, archive, export products, and distribution logs on normal exit or handled termination. It never uploads keys, signing material, archives, IPAs, or Xcode distribution logs as artifacts. GitHub's ephemeral runner disposal handles hard termination that cannot execute a shell trap.

Archive/upload failures intentionally do not dump potentially sensitive distribution logs. Check signing/profile setup, capability alignment, key access, and App Store Connect status. If deeper diagnostics are needed, reproduce on a trusted local Mac and inspect temporary logs while the command is running; never publish the raw logs. Do not rerun a build number Apple already accepted.

The release job currently performs no external group assignment, Beta App Review submission, or App Store submission. Upload completion is established only by the workflow's Xcode checks and Apple API verification, never inferred from generating an archive or installing a simulator build.

## Local checks

```bash
bash -n scripts/release/testflight.sh scripts/release/validate-ios.sh
python3 -m unittest discover -s scripts/release -p 'test_*.py'
ruby -c scripts/release/configure-signing.rb
```

The API tests use generated temporary EC keys and mocked API responses. They make no Apple requests and do not establish signing or upload success.
