# Native iOS simulator captures

These are actual iPhone and iPad simulator captures from the compiled iOS app,
exported from the unsigned native-validation artifact. They are not browser substitutes.

- Source repository: `dirkwbeveridge/grill-master`
- Source commit: `100927fa9defd395bdded5174d7440de659c5b1d`
- Source workflow run: https://github.com/dirkwbeveridge/grill-master/actions/runs/41408061553
- Source artifact: `native-ios-screenshots`
- Capture script: `scripts/release/capture-screenshots.py` at the source commit
- Capture method recorded by the script: debug launch argument; real native app
- Simulator runtime recorded by the capture script: iOS 26.2

| File | Simulator device | Debug destination | Launch arguments | Reported readiness | Native PNG dimensions |
| --- | --- | --- | --- | --- | --- |
| [iphone-configure.png](iphone-configure.png) | iPhone 17 Pro Max | `configure` | `--grill-route configure` | native route consumed by web bridge; 2s render wait | 1320 × 2868 |
| [iphone-temperatures.png](iphone-temperatures.png) | iPhone 17 Pro Max | `temperatures` | `--grill-route temperatures` | native route consumed by web bridge; 2s render wait | 1320 × 2868 |
| [ipad-configure.png](ipad-configure.png) | iPad Pro 13-inch (M5) | `configure` | `--grill-route configure` | native route consumed by web bridge; 2s render wait | 2064 × 2752 |
| [ipad-temperatures.png](ipad-temperatures.png) | iPad Pro 13-inch (M5) | `temperatures` | `--grill-route temperatures` | native route consumed by web bridge; 2s render wait | 2064 × 2752 |

## Capture protocol

The source capture script launches the real Debug app with `--grill-route` and the
requested destination. It removes prior-process readiness evidence, waits for a
fresh destination marker written when the web bridge consumes the native route,
then waits two seconds before taking the simulator PNG. The manifest reports that
handoff and wait; the exporter validates the report's exact fields and values.

This Debug-only launch path does not exercise open-URL confirmation dialogs, Siri,
or App Shortcuts. Those integrations require their own native tests. A readiness
marker does not verify rendered screen labels or establish visual acceptance.

## Acceptance still required

The manifest and PNG structure have been validated. A human must still open every
image and accept the actual screen, route, layout, safe areas, readable text, and
device dimensions. Export does not establish App Store screenshot acceptance or
native UI correctness. These captures target configure and temperature screens only;
they do not prove active-timer, queue, log, or locked-screen behavior.

- Simulator captures; physical device validation remains required.
- Debug launch routing does not validate open-URL prompts, Siri, or Shortcuts.
- Bridge consumption and render wait require visual screen-label verification.
- Active-cook screenshots require real UI automation and are not fabricated.

No signed archive, build log, signing material, or Apple credentials are included.
