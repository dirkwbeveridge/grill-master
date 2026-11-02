# Privacy source inventory

Reviewed November 2, 2026. This is static evidence for the release candidate, not
an App Store privacy declaration or a capture of native network traffic.

- `package-lock.json` and `ios/App/Podfile.lock` identify Capacitor 5.7.8 and
  Haptics, Local Notifications, and Preferences 5.0.8. No analytics, advertising,
  remote push, account backend, or cloud cooking-data SDK is declared.
- `www/index.html` bundles its styling and icon; the app's Support and Privacy
  links point to the public GitHub Pages site. No external font is loaded.
- `www/app.js` does not initiate HTTP requests for cooking features. App storage
  uses Capacitor Preferences or local web storage. Native shared cook snapshots
  use `UserDefaults(suiteName:)` for the fixed App Group.
- Main app and widget privacy manifests declare UserDefaults reasons `CA92.1`
  (own app preferences) and `1C8F.1` (shared App Group preferences), no collected
  data types, and no tracking. Capacitor's installed source includes its own
  UserDefaults manifest; CapacitorCordova includes an empty accessed-API list.
  Confirm all applicable manifests are actually included in the signed archive.
- Capacitor contains HTTP and asset-loading implementations. Their presence is
  network capability, not evidence that this app collects data; verify actual
  traffic in the submitted build, including allowed/denied notifications and
  external links. No blanket assertion of zero network activity is made.
- GitHub handles website requests and voluntary public issue submissions.
  Account for support practices under Apple's current disclosure rules before
  choosing the proposed “Data Not Collected” answer. Do not infer that answer
  solely from local cooking records or empty manifest collection arrays.

The legal operator, monitored private privacy/support contact, final App Privacy
answers, and final dependency/archive review remain pending. Runtime traffic,
platform backup behavior, and physical-device tests are not established here.
