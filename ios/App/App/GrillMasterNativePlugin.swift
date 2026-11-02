import ActivityKit
import Capacitor
import UIKit
import WidgetKit

/// Capacitor 5 discovers CAPBridgedPlugin conformances in the app executable.
@objc(GrillMasterNativePlugin)
public class GrillMasterNativePlugin: CAPPlugin, CAPBridgedPlugin {
    public let identifier = "GrillMasterNativePlugin"
    public let jsName = "GrillMasterNative"
    public let pluginMethods: [CAPPluginMethod] = [
        CAPPluginMethod(name: "syncCook", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "endCook", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "getStatus", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "consumeRoute", returnType: CAPPluginReturnPromise)
    ]
    private var routeObserver: NSObjectProtocol?
    private let operations = NativeCookOperationQueue.shared

    public override func load() {
        routeObserver = NotificationCenter.default.addObserver(forName: GrillRoute.notification, object: nil, queue: .main) { [weak self] note in
            guard let destination = note.object as? String else { return }
            self?.notifyListeners("route", data: ["destination": destination], retainUntilConsumed: true)
        }
    }

    deinit {
        if let routeObserver = routeObserver { NotificationCenter.default.removeObserver(routeObserver) }
    }

    @objc func consumeRoute(_ call: CAPPluginCall) {
        call.resolve(["destination": GrillRoute.consume() as Any? ?? NSNull()])
    }

    @objc func getStatus(_ call: CAPPluginCall) {
        if #available(iOS 16.2, *) {
            call.resolve(["supported": true, "activitiesEnabled": ActivityAuthorizationInfo().areActivitiesEnabled,
                          "activeActivities": Activity<GrillActivityAttributes>.activities.count])
        } else {
            call.resolve(["supported": false, "activitiesEnabled": false, "activeActivities": 0])
        }
    }

    @objc func syncCook(_ call: CAPPluginCall) {
        guard let value = call.getObject("cook"),
              let id = value["id"] as? String, !id.isEmpty,
              let title = value["title"] as? String, !title.isEmpty,
              let phase = value["phase"] as? String,
              let start = value["startedAt"] as? Double,
              let end = value["endsAt"] as? Double,
              let target = value["targetTemperature"] as? Double,
              let unit = value["unit"] as? String, ["F", "C"].contains(unit),
              let active = value["active"] as? Bool,
              start.isFinite, end.isFinite, target.isFinite, end >= start,
              (0...1000).contains(target) else {
            call.reject("Invalid cook summary", "INVALID_COOK")
            return
        }
        let cook = CookSnapshot(id: String(id.prefix(100)), title: String(title.prefix(80)), phase: String(phase.prefix(80)),
                                startedAt: Date(timeIntervalSince1970: start / 1000), endsAt: Date(timeIntervalSince1970: end / 1000),
                                targetTemperature: target, unit: unit, active: active, updatedAt: Date())
        operations.enqueue { [operations] revision in
            guard operations.isCurrent(revision) else {
                call.resolve(["synced": false, "liveActivity": false, "superseded": true])
                return
            }
            CookSharedStore.save(active ? cook : nil)
            if #available(iOS 14.0, *) { WidgetCenter.shared.reloadTimelines(ofKind: CookSharedStore.widgetKind) }
            if #available(iOS 16.2, *) {
                do {
                    let running = try await GrillLiveActivity.sync(cook, isCurrent: { operations.isCurrent(revision) })
                    call.resolve(["synced": true, "liveActivity": running])
                } catch {
                    // Widgets still receive the cook when the system declines a Live Activity.
                    call.resolve(["synced": true, "liveActivity": false, "reason": error.localizedDescription])
                }
            } else {
                call.resolve(["synced": true, "liveActivity": false])
            }
        }
    }

    @objc func endCook(_ call: CAPPluginCall) {
        operations.enqueue { _ in
            CookSharedStore.save(nil)
            if #available(iOS 14.0, *) { WidgetCenter.shared.reloadTimelines(ofKind: CookSharedStore.widgetKind) }
            if #available(iOS 16.2, *) { await GrillLiveActivity.endAll() }
            call.resolve(["ended": true])
        }
    }
}

/// MainActor alone permits interleaving at every ActivityKit await. The task chain
/// keeps each complete operation in invocation order, including across bridge reloads.
/// Revisions also stop a suspended sync from creating an activity after cancellation
/// or replacement has already been requested.
private final class NativeCookOperationQueue {
    static let shared = NativeCookOperationQueue()
    private let lock = NSLock()
    private var tail: Task<Void, Never>?
    private var revision: UInt64 = 0

    func enqueue(_ operation: @escaping @MainActor (UInt64) async -> Void) {
        lock.lock()
        revision &+= 1
        let operationRevision = revision
        let previous = tail
        tail = Task { @MainActor in
            await previous?.value
            await operation(operationRevision)
        }
        lock.unlock()
    }

    func isCurrent(_ expected: UInt64) -> Bool {
        lock.lock()
        defer { lock.unlock() }
        return revision == expected
    }
}

@available(iOS 16.2, *)
@MainActor
enum GrillLiveActivity {
    static func sync(_ cook: CookSnapshot, isCurrent: () -> Bool) async throws -> Bool {
        guard isCurrent() else { return false }
        guard cook.active else { await endAll(); return false }
        let state = GrillActivityAttributes.ContentState(phase: cook.phase, startedAt: cook.startedAt, endsAt: cook.endsAt,
                                                        targetTemperature: cook.targetTemperature, unit: cook.unit)
        let content = ActivityContent(state: state, staleDate: cook.endsAt)
        let activities = Activity<GrillActivityAttributes>.activities
        for activity in activities where activity.attributes.cookID != cook.id {
            await activity.end(nil, dismissalPolicy: .immediate)
            guard isCurrent() else { return false }
        }
        guard isCurrent() else { return false }
        if let activity = activities.first(where: { $0.attributes.cookID == cook.id }) {
            await activity.update(content)
            return isCurrent()
        }
        guard ActivityAuthorizationInfo().areActivitiesEnabled,
              UIApplication.shared.applicationState == .active else { return false }
        _ = try Activity.request(attributes: GrillActivityAttributes(cookID: cook.id, title: cook.title), content: content, pushType: nil)
        return true
    }

    static func endAll() async {
        for activity in Activity<GrillActivityAttributes>.activities {
            await activity.end(nil, dismissalPolicy: .immediate)
        }
    }
}
