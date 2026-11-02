# Release implementation status

Updated November 2, 2026 (UTC). App Store title: **Grill Master: Backyard Pro**.
The installed app keeps the short name Grill Master. Requested paid download:
**$0.99 USD**, still to be configured and verified in App Store Connect.

## Implemented and verified

- Timer/queue deadline recovery, independent reminders, FIFO acknowledgements,
  snoozing, pause/cancel handling, honest save errors, and minimum food temperatures.
- Responsive interface, larger controls, keyboard dialogs, local fonts/icon,
  and public support/privacy documents. Prior local Chromium and GitHub
  Chromium/WebKit runs passed. Browser native-service mocks are not device evidence.
- Siri/App Intents/Shortcuts, shared cook widget, Live Activities, native routes,
  privacy manifests, and serialized native activity operations are implemented.
  Unsigned SDK compilation passed; signed/device behavior remains pending.
- Forty Chromium app tests and sixty release-helper tests passed in the restored
  cloud environment. GitHub Chromium/WebKit run 41412394193 also passed.
- Main and widget identifiers were registered through the authorized Apple API key.
  The four existing GitHub environment secrets authenticate successfully. No
  Blueberry certificates, keys, profiles, or identifiers were revoked or changed.

## Current release attempt

- Source/native capture guard: `13109ea86cff0b97f7a55b535c0165f72bf57456`.
- Automatic TestFlight workflow:
  https://github.com/dirkwbeveridge/grill-master/actions/runs/41412396529
  This attempt failed in unsigned validation, before signing/upload started.
  Replacement validation with bounded diagnostics is run 41413184587
  (source f31e38c16a9e6c69ad8fb2ed1e21d5904c832091).
- The owner reports the shared App Group and new App Store Connect app complete.
  Fresh inventory run 41412398469 still cannot see an app matching
  `com.dirkbeveridge.grillmaster`. Bundle ID/Apple ID confirmation is pending.
  API authentication and both registered identifiers are confirmed; App Group
  membership is not yet independently established.
- Automatic signing uses the four existing secrets. It checks a signed archive's
  app/widget identifiers, versions, signatures, embedded profiles, and team/group
  entitlements before uploading, then verifies Apple visibility and What to Test.
  A failed provisioning attempt must be diagnosed before rerunning. Manual P12
  and profile secrets are a fallback, not an established requirement.
- No TestFlight upload, Apple review approval, or public App Store availability
  is established by the results recorded here.

## Screenshot and site evidence

- Native capture runs 41384119053 and 41408061553 compiled successfully, but visual
  review rejected the former's OS confirmation overlays and the latter's blank
  iPad configuration image. Neither is a complete accepted screenshot set.
- Replacement capture now retries actual simulator images until visible app
  content appears; it rejects persistent blank screens. This does not replace
  visual route/layout acceptance. No screenshot pixels or cook states are fabricated.
- Browser review evidence remains under `release/evidence/web-review/` and must
  not be submitted as native App Store screenshots.
- Pages deployments succeeded, including run 41412394164, but a competing legacy
  branch build was observed. The workflow now verifies `build_type=workflow` and
  checks the public home, support, privacy, and stylesheet after deployment.
  Its attempt to change that repository setting was denied by GitHub in run
  41412705882. Owner must select **GitHub Actions** in Settings → Pages → Source;
  the next deployment must pass public HTTP/content checks before acceptance.
- Direct cloud requests to GitHub API/Pages are restricted. Required network
  domains and reusable setup instructions are saved in the cloud configuration
  draft; saving a draft does not apply its policy to this instance.

## Remaining owner/account and device gates

Confirm app-record visibility, Pages source, legal rights holder and monitored
private privacy/support contact; complete Paid Apps agreement, tax/banking,
trader/territory decisions, price, age/privacy/export questionnaires, and private
App Review contact. Validate the final signed app, lock-screen/background
notifications, VoiceOver, large text, widgets, Siri/Shortcuts, and TestFlight
installation on physical devices. Apple processing and review are external gates.

See `privacy-and-release-checklist.md`, `screenshot-plan.md`, and
`../scripts/release/README.md` for remaining checks and the release workflow.
