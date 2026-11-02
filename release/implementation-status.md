# Release implementation status

## Implemented and locally verified

- Main and queue timer recovery, independent alerts, lane snoozing, FIFO acknowledgements, safe-temperature guidance, save error recovery, and keyboard dialogs.
- Forty Chromium foundation/runtime tests passed in one combined run; seven release-helper API/cryptographic tests passed. Native services in browser tests are mocks, not device evidence.
- Accessible/responsive shared interface, bundled offline icon/system fonts, public support/privacy site source, and App Store metadata/review drafts.
- Native Siri/App Shortcuts, widget, Live Activity, deep-link bridge, App Group configuration and privacy manifests are implemented. Swift syntax, Xcode project structure, and plist/XML checks passed; Apple SDK compilation is still pending.
- Independent native review found a cancellation race; native and JavaScript operation ordering were corrected and re-reviewed.
- Browser, unsigned native validation/screenshot, Pages, and manual validation-gated TestFlight workflows are prepared.

## Publication and Apple gates

- Review branch: `codex/app-store-readiness`. Web and unsigned native validation run on pushes to that branch and `main`. Pages production deployment is limited to `main` or deliberate manual dispatch after repository settings are configured.
- Git read/write works through the existing HTTPS Git proxy. The current cloud network denies `api.github.com` (CONNECT 403). Necessary domains were saved in the environment draft; they have not been observed applied. Apply the saved network settings to enable PR/API operations and public-site verification.
- GitHub Pages is not yet confirmed enabled or published. Do not treat intended support/privacy URLs as live without HTTPS checks.
- Native App Store screenshots have not yet been captured. The macOS workflow captures actual installed app screens on iPhone and iPad; `release/evidence/web-review/` is only browser review evidence.
- This cloud host is Linux with no Xcode or injected Apple signing/App Store Connect bindings. TestFlight upload has not occurred. Configure the secure `testflight` Actions environment and the eight secrets described in `scripts/release/README.md`, with matching App Group profiles for both targets.
- Legal operator/private support contact, Apple account agreements, tax/banking/trader decisions, price/territories, and review contact remain owner inputs. The requested base price is $0.99 USD; it has not been set in App Store Connect.
- Physical-device tests, final SDK/privacy/export validation, Apple processing/review, and public App Store release remain outstanding. A source commit or TestFlight upload does not establish approval or public availability.

See `privacy-and-release-checklist.md`, `screenshot-plan.md`, and `../scripts/release/README.md` for the concrete remaining steps.
