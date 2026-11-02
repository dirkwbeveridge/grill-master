# Native iOS simulator captures

These are actual iPhone and iPad simulator captures from the compiled iOS app,
exported from the unsigned native-validation artifact. They are not browser substitutes.

- Source repository: `dirkwbeveridge/grill-master`
- Source commit: `cb52b374bd21963bf390f5917cfa2cb2520bb0cc`
- Source workflow run: https://github.com/dirkwbeveridge/grill-master/actions/runs/41384119053
- Source artifact: `native-ios-screenshots`
- Capture script: `scripts/release/capture-screenshots.py` at the source commit
- Simulator runtime recorded by the capture script: iOS 26.2

| File | Simulator device | Route | Native PNG dimensions |
| --- | --- | --- | --- |
| [iphone-configure.png](iphone-configure.png) | iPhone 17 Pro Max | `grillmaster://configure` | 1320 × 2868 |
| [iphone-temperatures.png](iphone-temperatures.png) | iPhone 17 Pro Max | `grillmaster://temperatures` | 1320 × 2868 |
| [ipad-configure.png](ipad-configure.png) | iPad Pro 13-inch (M5) | `grillmaster://configure` | 2064 × 2752 |
| [ipad-temperatures.png](ipad-temperatures.png) | iPad Pro 13-inch (M5) | `grillmaster://temperatures` | 2064 × 2752 |

## Acceptance still required

The manifest and PNG structure have been validated. A human must still open every
image and accept the actual screen, route, layout, safe areas, readable text, and
device dimensions. Export does not establish App Store screenshot acceptance or
native UI correctness. These captures show configure and temperature routes only;
they do not prove active-timer, queue, log, or locked-screen behavior.

- Simulator captures; physical device validation remains required.
- Active-cook screenshots require real UI automation and are not fabricated.

No signed archive, build log, signing material, or Apple credentials are included.
