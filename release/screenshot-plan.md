# Native App Store screenshot plan

Capture the final iOS build running in **iOS Simulator**, for both iPhone and iPad while both are supported. Browser captures and resized browser images are design evidence only; do not submit them as native app screenshots. The existing repository screenshots are not accepted as verified App Store evidence by this plan.

## Capture setup

1. Build/install the exact release candidate with a supported Xcode and the target simulator runtime. Record commit, native version/build, Xcode/SDK, simulator model, runtime, orientation, and pixel dimensions.
2. Check App Store Connect’s current screenshot requirements for the device families in this app record. Capture an accepted large iPhone display and an accepted large iPad display at their native simulator sizes. Common examples are a 6.9-inch iPhone at 1320 × 2868 and a 13-inch iPad at 2064 × 2752; **verify current accepted dimensions rather than assuming these examples satisfy the account’s requirements**.
3. For each supported orientation, use a deliberate consistent status bar and readable text size. Example status-bar override: `xcrun simctl status_bar booted override --time '9:41' --dataNetwork wifi --wifiMode active --wifiBars 3 --batteryState charged --batteryLevel 100`.
4. Seed only synthetic, nonpersonal cook records through the real UI or a documented screenshot fixture. Remove debug labels, logs, simulated permission prompts, private account information, and unresolved errors. Do not fabricate features or success states in a graphic editor.
5. Use Simulator’s native capture, for example `xcrun simctl io booted screenshot /absolute/path/to/screenshot.png`. Capture each device class separately. Reset the status-bar override after capture with `xcrun simctl status_bar booted clear`.
6. Inspect every full-resolution image for native safe areas, text clipping, orientation/layout, keyboard remnants, status bar, and truthful settings. Record dimensions and capture provenance. Retain raw originals; export an accepted PNG/JPEG without alpha if required by App Store Connect.

## Storyboard

| Order | Native state | Suggested caption | Truth check |
| --- | --- | --- | --- |
| 1 | Configured Timer cook card, just before Start Cook | Plan your next cook | Show real cut/thickness/heat settings and generated times; don't imply these estimate safety. |
| 2 | Active main timer on Side A or Side B | Follow every stage | Use the actual timer UI; no invented Live Activity or lock-screen view. |
| 3 | Queue with two distinguishable synthetic items | Keep the grill organized | Distinct item names/states; verify controls and native reminders separately. |
| 4 | Log with a small set of synthetic saved cooks | Keep the cooks worth repeating | Use actual persistence and supported record fields. |
| 5 | Temperature guide showing safety guidance | Check with a thermometer | All visible food-temperature guidance must pass the final safety review. |

Capture all five on iPhone and iPad if the store accepts that count. Keep the first screenshots focused on the actual app UI; optional captions must not obscure controls or make unproven claims. Store screenshots must match the binary and supported device family. Do not include a price in screenshot art; regional prices can differ.

## Accessibility and native verification beside the screenshot session

- Run VoiceOver through setup, timer, queue, saved cooks, and dialogs.
- Check accessibility text sizes, increased contrast, Reduce Motion, and keyboard focus.
- On iPad check supported rotations, window resizing, safe areas, and a layout that uses available width.
- Test foreground/background/locked-screen timers on physical hardware. A simulator screenshot cannot validate delivery reliability.

## Deliverables and completion record

Save raw images under a release-evidence location chosen by the release owner, grouped by device model. Record each filename’s screen, dimensions, source device/runtime, commit, version/build, and capture time. Keep screenshot artifacts separate from the public `docs/` site unless deliberately reviewed for publication.

**Status: replacement capture in progress.** Native compilation and captures succeeded
in runs 41384119053 and 41408061553. Visual inspection rejected the first set's
temperature images because of an OS open-URL dialog. The second set fixed that
routing issue but its iPad configuration image still shows a blank launch view.
Neither set is accepted as a complete submission set. The current capture script
retries actual simulator screenshots until visible app content appears and fails
if the image remains blank. This guard does not establish screen semantics;
inspect every replacement image before acceptance. Browser review images remain
separate from native submission evidence.
