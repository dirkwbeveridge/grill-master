import AppIntents

@available(iOS 16.0, *)
struct ConfigureCookIntent: AppIntent {
    static var title: LocalizedStringResource = "Configure a Cook"
    static var description = IntentDescription("Open Grill Master to choose your cut and configure a cook.")
    static var openAppWhenRun = true

    @MainActor func perform() async throws -> some IntentResult {
        GrillRoute.queue("configure")
        return .result()
    }
}

@available(iOS 16.0, *)
struct OpenActiveCookIntent: AppIntent {
    static var title: LocalizedStringResource = "Open Active Cook"
    static var description = IntentDescription("Open the current cook in Grill Master, or configure one if no cook is active.")
    static var openAppWhenRun = true

    @MainActor func perform() async throws -> some IntentResult {
        GrillRoute.queue("active")
        return .result()
    }
}

@available(iOS 16.0, *)
struct OpenTemperatureGuideIntent: AppIntent {
    static var title: LocalizedStringResource = "Open Temperature Guide"
    static var description = IntentDescription("Open the temperature reference in Grill Master.")
    static var openAppWhenRun = true

    @MainActor func perform() async throws -> some IntentResult {
        GrillRoute.queue("temperatures")
        return .result()
    }
}

@available(iOS 16.0, *)
struct GrillMasterShortcuts: AppShortcutsProvider {
    static var shortcutTileColor: ShortcutTileColor = .orange

    static var appShortcuts: [AppShortcut] {
        AppShortcut(intent: ConfigureCookIntent(), phrases: ["Configure a cook in \(.applicationName)", "Start grilling with \(.applicationName)"], shortTitle: "Configure Cook", systemImageName: "flame")
        AppShortcut(intent: OpenActiveCookIntent(), phrases: ["Open my cook in \(.applicationName)", "Check my cook in \(.applicationName)"], shortTitle: "Active Cook", systemImageName: "timer")
        AppShortcut(intent: OpenTemperatureGuideIntent(), phrases: ["Open temperatures in \(.applicationName)"], shortTitle: "Temperature Guide", systemImageName: "thermometer.medium")
    }
}
