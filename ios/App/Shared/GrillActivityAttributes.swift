import ActivityKit
import Foundation

@available(iOS 16.2, *)
struct GrillActivityAttributes: ActivityAttributes {
    struct ContentState: Codable, Hashable {
        let phase: String
        let startedAt: Date
        let endsAt: Date
        let targetTemperature: Double
        let unit: String

        var temperatureLabel: String { "\(Int(targetTemperature.rounded()))°\(unit)" }
    }

    let cookID: String
    let title: String
}
