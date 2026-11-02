# Grill Master

A grilling timer and cook log with a Capacitor iOS app. Choose a cut, review an estimated cook plan, follow sear/finish/rest stages, and keep the cooks worth repeating.

Cooking times are estimates. The app does not measure food temperature. Use a food thermometer and follow the safe minimum temperatures for the food being cooked.

## Development

The web interface lives in `www/`. It uses local assets and system fonts, with no web build step, backend, or account requirement. Node 24 and npm 11 were validated in the cloud workspace.

```bash
npm ci
npm run serve
```

The development server uses port 4173. Use the existing checkout; cloud tasks are already isolated and do not need an additional Git worktree unless requested.

### Tests

```bash
npx playwright install --with-deps chromium webkit
npm test -- --workers=2
```

The suite includes foundation flows and regressions for safe-temperature guidance, timer recovery, independent queue alerts, simultaneous expiries, snoozing, failed saves, native bridge ordering, and keyboard dialogs. The `iphone` project uses WebKit; `mobile-chromium` uses Chromium with an iPhone viewport and touch emulation. Browser tests do not validate native iOS notifications or ActivityKit.

When using the cloud image's installed Chromium:

```bash
PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/usr/bin/chromium npm run test:chromium
```

Use `npm run test:webkit` after installing WebKit. The default test run excludes screenshot/icon generators because those overwrite committed artwork. Browser test artifacts are ignored.

## App behavior

- Main and queued cooks retain their configuration, deadlines, paused state, and pending acknowledgements locally.
- Returning after an expired stage asks for acknowledgement rather than automatically advancing food through unattended stages.
- Queue timers schedule independent local notifications on native iOS. Notification denial or scheduling failures are shown in the app.
- Cook history and runtime state use Capacitor Preferences when available, otherwise browser local storage. There is no app-provided cloud sync; system backups depend on device settings.
- The interface supports narrow screens, tablet layouts, text scaling, keyboard dialogs, and reduced motion. Native VoiceOver, large text, and real-device testing remain release gates.

## iOS and system integrations

The Xcode workspace is `ios/App/App.xcworkspace`, shared scheme `App`. Native sources include three App Shortcuts (configure cook, open active cook, open temperature guide), a current-cook widget, and a Live Activity/Dynamic Island presentation. A Capacitor bridge shares a small current-cook snapshot with the extension. The custom URLs are `grillmaster://configure`, `grillmaster://active`, and `grillmaster://temperatures`.

The app deployment target is iOS 13; App Intents are gated to iOS 16, and the widget/Live Activity extension requires iOS 16.2. Native integration source and project structure were reviewed on Linux; unsigned Apple SDK compilation and simulator capture succeeded in the macOS validation workflow. Device behavior and signed release validation remain pending. A Live Activity displays the current stage deadline and marks an overdue snapshot stale; it does not silently advance cooking stages in the background.

On a Mac with Xcode and CocoaPods:

```bash
npm ci
npx cap sync ios
bash scripts/release/validate-ios.sh
```

See [native validation and TestFlight setup](scripts/release/README.md) for signing, App Group provisioning, secure GitHub Actions secrets, genuine simulator screenshots, archive/upload, and independent Apple API verification. Never commit credentials or signing artifacts.

## Public documents and distribution

`docs/` contains the static home, support, and privacy pages. The Pages workflow publishes this directory from `main` after GitHub Pages is configured to use GitHub Actions. GitHub reports a successful Pages deployment at these URLs. Direct cloud HTTP/content checks remain blocked by the current network policy:

- https://dirkwbeveridge.github.io/grill-master/
- https://dirkwbeveridge.github.io/grill-master/support/
- https://dirkwbeveridge.github.io/grill-master/privacy/

The installed iOS app bundles `www/`; it does not need GitHub Pages or Vercel to run. Apple handles the paid download. The requested base price is $0.99 USD, configured in App Store Connect after paid-app agreements, tax, and banking setup.

See the [release handoff](release/README.md) for listing copy, review notes, privacy/account decisions, and screenshot requirements. TestFlight upload, App Review approval, and public availability are separate outcomes and must be recorded from actual Apple results.

MIT license; see [LICENSE](LICENSE).
