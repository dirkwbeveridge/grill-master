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
  Diagnostic validation run 41413184587 confirmed simulator compilation succeeded,
  then failed because a capture remained blank. Replacement validation is run
  41414814002 (source 3fa30624f63067c0273aa9744ebf347ab4aee2a5).
  It records rejected images separately and permits one bounded app relaunch.
  The screenshot export workflow waits for that exact run, rejects failed runs,
  and can preserve only its four validated PNGs and public provenance on
  `codex/native-screenshots-v3`. Visual acceptance is still required.
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
