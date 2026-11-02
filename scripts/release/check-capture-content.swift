import AppKit
import Foundation

// Reject a launch screen or blank WebView. This is not a screen-label or layout test.
guard CommandLine.arguments.count == 2,
      let data = try? Data(contentsOf: URL(fileURLWithPath: CommandLine.arguments[1])),
      let bitmap = NSBitmapImageRep(data: data) else {
    exit(2)
}
var samples = 0
var foreground = 0
// Ignore system status, home indicator, and edge spinners.
for y in stride(from: bitmap.pixelsHigh / 10, to: bitmap.pixelsHigh * 9 / 10, by: 8) {
    for x in stride(from: bitmap.pixelsWide / 10, to: bitmap.pixelsWide * 9 / 10, by: 8) {
        guard let color = bitmap.colorAt(x: x, y: y)?.usingColorSpace(.deviceRGB) else {
            exit(2)
        }
        samples += 1
        if color.redComponent > 0.20 || color.greenComponent > 0.15 || color.blueComponent > 0.15 {
            foreground += 1
        }
    }
}
// The real configuration and temperature screens contain substantial text/controls.
exit(samples > 0 && Double(foreground) / Double(samples) >= 0.015 ? 0 : 1)
