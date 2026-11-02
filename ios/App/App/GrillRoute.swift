import Foundation

enum GrillRoute {
    static let notification = Notification.Name("GrillMasterRoute")
    private static let pendingKey = "pendingRoute.v1"
    private static let pendingLock = NSLock()
    private static var pendingDestination: String?
    static let destinations: Set<String> = ["configure", "active", "temperatures"]

    static func queue(_ destination: String) {
        guard destinations.contains(destination) else { return }
        pendingLock.lock()
        pendingDestination = destination
        CookSharedStore.defaults?.set(destination, forKey: pendingKey)
        pendingLock.unlock()
        NotificationCenter.default.post(name: notification, object: destination)
    }

    static func consume() -> String? {
        pendingLock.lock()
        let destination = pendingDestination ?? CookSharedStore.defaults?.string(forKey: pendingKey)
        pendingDestination = nil
        CookSharedStore.defaults?.removeObject(forKey: pendingKey)
        pendingLock.unlock()
        let validated = destination.flatMap { destinations.contains($0) ? $0 : nil }
        #if DEBUG
        if let validated = validated, validated == debugLaunchDestination {
            writeDebugReadiness(destination: validated)
        }
        #endif
        return validated
    }

    static func handle(_ url: URL) -> Bool {
        guard url.scheme?.lowercased() == "grillmaster",
              let destination = url.host, destinations.contains(destination) else { return false }
        queue(destination)
        return true
    }

    #if DEBUG
    private static var debugLaunchDestination: String?

    /// Simulator capture enters the real route handoff without an OS open-URL dialog.
    /// The argument and readiness marker do not exist in Release builds.
    static func queueDebugLaunchRoute(arguments: [String] = ProcessInfo.processInfo.arguments) {
        guard let argument = arguments.firstIndex(of: "--grill-route"),
              arguments.indices.contains(argument + 1),
              destinations.contains(arguments[argument + 1]) else { return }
        let destination = arguments[argument + 1]
        debugLaunchDestination = destination
        if let marker = debugReadinessURL {
            try? FileManager.default.removeItem(at: marker)
        }
        queue(destination)
    }

    private static var debugReadinessURL: URL? {
        FileManager.default.urls(for: .cachesDirectory, in: .userDomainMask).first?.appendingPathComponent("GrillMaster", isDirectory: true)
            .appendingPathComponent("debug-route-ready.json")
    }

    private static func writeDebugReadiness(destination: String) {
        guard let marker = debugReadinessURL,
              let data = try? JSONSerialization.data(withJSONObject: [
                "destination": destination,
                "readiness": "native route consumed by web bridge"
              ]) else { return }
        do {
            try FileManager.default.createDirectory(at: marker.deletingLastPathComponent(), withIntermediateDirectories: true)
            try data.write(to: marker, options: .atomic)
        } catch {
            // Capture fails closed if its readiness marker cannot be written.
        }
    }
    #endif
}
