# Privacy, account, and release checklist

This checklist separates prepared repository material from account answers and native evidence that must be completed by the release owner. A checked item must have evidence for the final submitted build. Source inspection alone is insufficient for runtime claims.

## Public documents and hosting

- [x] Static home, support, and privacy pages are prepared in `docs/` with local CSS and no third-party resources loaded by the pages.
- [x] Support points to the actual repository: https://github.com/dirkwbeveridge/grill-master/issues.
- [x] A GitHub Actions Pages workflow publishes only `docs/`, on changes to `main` or manual workflow dispatch. It does not publish the application bundle or sell the app.
- [x] Source review confirms external fonts were removed. See [privacy source inventory](privacy-source-inventory.md); final binary and native traffic verification remain pending.
- [ ] Confirm timer/queue persistence matches the policy’s local session-storage description.
- [ ] Enable repository Pages with **GitHub Actions** as the source. Confirm the `github-pages` environment permits the intended deployment branch and the account/repository plan supports Pages.
- [ ] Complete an authorized deployment; verify all three public pages and the local stylesheet return successfully over HTTPS at the intended subpath.
- [ ] Verify in-app Support and Privacy links open these exact production URLs.
- [ ] Release owner: confirm the legal operator/rights holder and jurisdiction-specific privacy notice requirements. **Legal operator name/address and a monitored private privacy/contact email are PENDING**; add any legally required fields to the policy before launch. GitHub Issues is public and is not a private contact channel.
- [ ] Confirm the person operating the app can respond to privacy/support requests and that public support meets applicable App Store requirements. No response-time promise has been made.

Intended URLs:

- Home: https://dirkwbeveridge.github.io/grill-master/
- Support: https://dirkwbeveridge.github.io/grill-master/support/
- Privacy: https://dirkwbeveridge.github.io/grill-master/privacy/

## App privacy answers and manifest

- [ ] Audit the final app and every dependency for collection, outbound requests, tracking, required-reason APIs, and embedded SDK privacy manifests.
- [ ] Verify the app has no analytics/advertising SDK, tracking identifiers, account backend, telemetry, or uploaded cook data. Inspect actual native traffic with local notifications permitted and denied.
- [ ] **Proposed App Privacy answer: “Data Not Collected” only if that final audit supports Apple’s definition.** Local-only preferences are not automatically developer collection. GitHub website requests and voluntarily submitted support data need their own handling assessment. If support/feedback data is collected in a way Apple requires disclosed, answer the appropriate data types and purposes truthfully.
- [ ] Review the current Apple rules for optional customer-support disclosures and third-party service practices before finalizing answers. Do not select “not collected” solely because there is no app account.
- [ ] Inspect the archive for `PrivacyInfo.xcprivacy` and declared required-reason API usage, including Preferences/UserDefaults. Review every declared reason against actual behavior; a manifest is not a substitute for App Privacy answers.
- [ ] If notifications are local only, confirm there is no remote push service or unsolicited data transfer. Confirm requested permissions match real features.
- [ ] Verify data deletion/clear controls and their exact user-visible effects. Current policy avoids promising a delete button that may not exist. Explain OS backup/offload behavior accurately.
- [ ] Confirm privacy policy URL and in-app privacy link are accessible without sign-in.

## Age rating and content

- [ ] Complete the current App Store Connect age-rating questionnaire for the final binary; do not treat a proposed rating as assigned by Apple.
- [ ] Assess every prompt about unrestricted web access, user-generated content, advertising, messaging, contests, medical/treatment information, violence, substances, and other regulated content against the app itself. External GitHub support is not an in-app social feed; classify links as Apple's current questionnaire requires.
- [ ] Intended audience: general cooking-tool users. **Provisional expectation: lowest applicable rating if the completed questionnaire supports it.** No “Kids Category” submission or child-directed privacy claim is proposed.
- [ ] Review food-safety guidance for turkey burgers/poultry, ground meat, whole cuts, seafood, and rest periods. Estimated duration or preferred doneness must not claim safety. Verify the final app requires thermometer confirmation where intended.

## Export compliance

- [ ] Inventory cryptography in the final app and dependencies, including network transport, any custom crypto, and any features added during release work.
- [ ] Answer App Store Connect’s export-compliance questions for that inventory and the release owner’s legal situation. Standard operating-system HTTPS alone may qualify for an exemption, but do not assume all code qualifies.
- [ ] Set `ITSAppUsesNonExemptEncryption` to `NO` only after confirming the app does not use non-exempt encryption. Otherwise provide the appropriate classification/documentation and answers. **Final determination is PENDING.**
- [ ] Confirm regional distribution restrictions and any required declarations with the account owner.

## Paid download and account records

- [ ] Active Apple Developer Program membership and a real App Store Connect app record.
- [ ] Registered bundle ID, signing identity/profiles, final version/build, content rights, copyright owner, and review contact name/email/phone.
- [ ] Active Paid Apps agreement and completed tax/banking information.
- [ ] Set the available **$0.99 USD base price** and verify territory availability, currency/tax adjustments, commission terms, and net proceeds in the account. No payment gateway is needed just to charge for the download.
- [ ] Choose release timing and availability; do not assume automatic public release from uploading to TestFlight.
- [ ] If distributing in the EU or other territories requiring trader/business details, complete the applicable seller verification and disclosures. **Trader status/business contact details are PENDING owner answers.**
- [ ] Upload native screenshots and final copy, set support/privacy URLs, choose applicable categories, and complete accessibility disclosures only for features verified on supported devices.
- [ ] Review Apple’s current Xcode/SDK upload requirements and App Review Guidelines at submission time. Current requirements have not been verified by this document.

## Native release gate

- [ ] Signed Release archive builds/validates with intended app family, deployment target, version/build, icons, privacy manifests, and compatible plugins.
- [ ] Review background modes/entitlements against actual behavior; do not enable audio background mode solely to keep JavaScript timers running.
- [ ] Test timer recovery, queue notifications, simultaneous expiries, snooze routing, pause/cancel, save failures, permission denial, large text, VoiceOver, keyboard focus, offline assets, and iPad adaptation.
- [ ] Complete physical-device locked/background notification tests and TestFlight installation testing.
- [ ] Check App Review notes against the actual binary and publish no unvalidated Siri/Live Activities claims.
- [ ] Submit only after remaining gates are satisfied. Apple’s approval is an external dependency, not a repository test result.

## External dependencies still required

Repository changes cannot supply private App Store Connect account data, agreements, banking/tax/trader answers, legal identity/contact decisions, Apple signing authority, a supported macOS/Xcode environment, native device/simulator evidence, Apple's processing/review decisions, or a successful public Pages deployment. Those outcomes must be recorded when actually completed.
