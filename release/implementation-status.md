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

- Automatic TestFlight run [41418352647](https://github.com/dirkwbeveridge/grill-master/actions/runs/41418352647)
  used source `9d924f9d4ae53e42691876ec2741329468be1e01`. Unsigned compilation
  passed, and Apple preflight confirmed the exact app and unused build 2.
  Xcode then stopped with an authentication/authorization error during automatic
  signing. No upload occurred. Do not repeat the same signing attempt without
  diagnosing or correcting that failure.
- Read-only follow-up [41419209706](https://github.com/dirkwbeveridge/grill-master/actions/runs/41419209706)
  confirmed API authentication, the exact app record, both bundle IDs, both App
  Groups capabilities, and that the configured Team ID matches an accessible
  distribution certificate. No active App Store profiles exist for either target.
  API success does not establish that Xcode signing authentication succeeds.
  Diagnose on a trusted Mac, or use the existing manual signing workflow with
  securely supplied certificate/private key and two matching profiles.
- Store screenshot capture is separate from internal TestFlight upload. Run
  41414814002 compiled but rejected blank iPad configuration images even after
  one relaunch. Its `native-ios-capture-diagnostics` artifact retains rejected
  PNGs. The exporter correctly refused the failed run; no v3 set was accepted.
- The owner supplied Apple ID 6829659639. Direct API read-back confirmed the
  approved listing name and actual registered bundle ID `com.dbeveridge.grillmaster`
  in run 41416629827. The originally supplied bundle spellings did not match.
  Project and helpers now use that registered ID and `.widgets` for the extension.
  The owner confirmed shared App Group `group.com.dbeveridge.grillmaster`.
  App/widget entitlements, shared storage, and archive verification use that exact
  group. Both registered app IDs and the main app capability are confirmed;
  widget capability was created and read-back verified in run 41417111557.
  The signed archive must still establish both group associations.
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
  content appears and permits one bounded relaunch; it rejects persistent blank
  screens. Launch attempts are recorded and cold-launch reliability remains open. This does not replace
  visual route/layout acceptance. No screenshot pixels or cook states are fabricated.
- Browser review evidence remains under `release/evidence/web-review/` and must
  not be submitted as native App Store screenshots.
- Pages run [41419214890](https://github.com/dirkwbeveridge/grill-master/actions/runs/41419214890)
  verified workflow publishing as the sole source, deployed `docs/`, and passed
  live HTTPS/content checks for home, support, privacy, and stylesheet. The public
  site is https://dirkwbeveridge.github.io/grill-master/.
- Direct cloud requests to GitHub API/Pages are restricted. Required network
  domains and reusable setup instructions are saved in the cloud configuration
  draft; saving a draft does not apply its policy to this instance.

## Remaining owner/account and device gates

Resolve Xcode signing authentication, confirm the legal rights holder and monitored
private privacy/support contact; complete Paid Apps agreement, tax/banking,
trader/territory decisions, price, age/privacy/export questionnaires, and private
App Review contact. Validate the final signed app, lock-screen/background
notifications, VoiceOver, large text, widgets, Siri/Shortcuts, and TestFlight
installation on physical devices. Apple processing and review are external gates.

See `privacy-and-release-checklist.md`, `screenshot-plan.md`, and
`../scripts/release/README.md` for remaining checks and the release workflow.
