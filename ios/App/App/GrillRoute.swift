import Foundation

enum GrillRoute {
    static let notification = Notification.Name("GrillMasterRoute")
    private static let pendingKey = "pendingRoute.v1"
    static let destinations: Set<String> = ["configure", "active", "temperatures"]

    static func queue(_ destination: String) {
        guard destinations.contains(destination) else { return }
        CookSharedStore.defaults?.set(destination, forKey: pendingKey)
        NotificationCenter.default.post(name: notification, object: destination)
    }

    static func consume() -> String? {
        let destination = CookSharedStore.defaults?.string(forKey: pendingKey)
        CookSharedStore.defaults?.removeObject(forKey: pendingKey)
        return destination.flatMap { destinations.contains($0) ? $0 : nil }
    }

    static func handle(_ url: URL) -> Bool {
        guard url.scheme?.lowercased() == "grillmaster",
              let destination = url.host, destinations.contains(destination) else { return false }
        queue(destination)
        return true
    }
}
