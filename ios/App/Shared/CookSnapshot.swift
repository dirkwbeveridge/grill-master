import Foundation

/// Only the current cook summary crosses the app-group boundary; the web app owns the cook.
struct CookSnapshot: Codable {
    let id: String
    let title: String
    let phase: String
    let startedAt: Date
    let endsAt: Date
    let targetTemperature: Double
    let unit: String
    let active: Bool
    let updatedAt: Date

    var temperatureLabel: String { "\(Int(targetTemperature.rounded()))°\(unit)" }
}

enum CookSharedStore {
    static let appGroup = "group.com.dirkbeveridge.grillmaster"
    static let widgetKind = "GrillMasterCook"
    static let cookKey = "currentCook.v1"

    static var defaults: UserDefaults? { UserDefaults(suiteName: appGroup) }

    static func read() -> CookSnapshot? {
        guard let data = defaults?.data(forKey: cookKey) else { return nil }
        return try? JSONDecoder().decode(CookSnapshot.self, from: data)
    }

    static func save(_ cook: CookSnapshot?) {
        if let cook = cook, let data = try? JSONEncoder().encode(cook) {
            defaults?.set(data, forKey: cookKey)
        } else {
            defaults?.removeObject(forKey: cookKey)
        }
    }
}
