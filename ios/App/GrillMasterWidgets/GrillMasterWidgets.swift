import ActivityKit
import SwiftUI
import WidgetKit

private let ember = Color(red: 0.87, green: 0.39, blue: 0.12)

struct CookEntry: TimelineEntry {
    let date: Date
    let cook: CookSnapshot?
}

struct CookProvider: TimelineProvider {
    func placeholder(in context: Context) -> CookEntry { CookEntry(date: Date(), cook: nil) }

    func getSnapshot(in context: Context, completion: @escaping (CookEntry) -> Void) {
        completion(CookEntry(date: Date(), cook: CookSharedStore.read()))
    }

    func getTimeline(in context: Context, completion: @escaping (Timeline<CookEntry>) -> Void) {
        let now = Date()
        let cook = CookSharedStore.read()
        var entries = [CookEntry(date: now, cook: cook)]
        if let cook = cook, cook.endsAt > now {
            entries.append(CookEntry(date: cook.endsAt, cook: cook))
        }
        completion(Timeline(entries: entries, policy: .after(now.addingTimeInterval(15 * 60))))
    }
}

struct CookWidgetView: View {
    let entry: CookEntry

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Label("GRILL MASTER", systemImage: "flame.fill")
                .font(.caption2.weight(.bold))
                .foregroundStyle(ember)
            if let cook = entry.cook, cook.active {
                Text(cook.title).font(.headline).lineLimit(2)
                Text(cook.phase).font(.caption).lineLimit(1)
                HStack {
                    if cook.endsAt > entry.date {
                        Text(timerInterval: cook.startedAt...cook.endsAt, countsDown: true)
                            .monospacedDigit()
                    } else {
                        Text("Check your cook")
                    }
                    Spacer(minLength: 4)
                    Text(cook.temperatureLabel)
                }
                .font(.title3.weight(.semibold))
                Text("Target · verify with a thermometer").font(.caption2).foregroundStyle(.secondary)
            } else {
                Text("Your next great cook.").font(.headline)
                Text("Choose a cut and make a plan.").font(.caption).foregroundStyle(.secondary)
                Label("Configure cook", systemImage: "arrow.up.right").font(.caption.weight(.semibold)).foregroundStyle(ember)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .leading)
        .padding()
        .widgetURL(URL(string: entry.cook?.active == true ? "grillmaster://active" : "grillmaster://configure"))
        .cookWidgetBackground()
    }
}

private extension View {
    @ViewBuilder func cookWidgetBackground() -> some View {
        if #available(iOSApplicationExtension 17.0, *) {
            self.containerBackground(for: .widget) { Color(red: 0.08, green: 0.055, blue: 0.04) }
        } else {
            self.background(Color(red: 0.08, green: 0.055, blue: 0.04))
        }
    }
}

struct GrillMasterCookWidget: Widget {
    var body: some WidgetConfiguration {
        StaticConfiguration(kind: CookSharedStore.widgetKind, provider: CookProvider()) { entry in
            CookWidgetView(entry: entry).preferredColorScheme(.dark)
        }
        .configurationDisplayName("Current Cook")
        .description("Open your cook and see its stage, remaining time, and target temperature.")
        .supportedFamilies([.systemSmall, .systemMedium])
    }
}

struct GrillMasterLiveActivity: Widget {
    var body: some WidgetConfiguration {
        ActivityConfiguration(for: GrillActivityAttributes.self) { context in
            VStack(alignment: .leading, spacing: 8) {
                HStack {
                    Label("Grill Master", systemImage: "flame.fill").foregroundStyle(ember)
                    Spacer()
                    Text(context.state.temperatureLabel).fontWeight(.semibold)
                }
                Text(context.attributes.title).font(.headline)
                HStack {
                    Text(context.isStale ? "Check your cook" : context.state.phase)
                    Spacer()
                    if !context.isStale {
                        Text(timerInterval: context.state.startedAt...context.state.endsAt, countsDown: true).monospacedDigit()
                    }
                }
                Text("Target temperature · verify with a thermometer").font(.caption2).foregroundStyle(.secondary)
            }
            .padding()
            .activityBackgroundTint(Color(red: 0.08, green: 0.055, blue: 0.04))
            .activitySystemActionForegroundColor(.white)
            .foregroundStyle(.white)
            .widgetURL(URL(string: "grillmaster://active"))
        } dynamicIsland: { context in
            DynamicIsland {
                DynamicIslandExpandedRegion(.leading) {
                    Label("Grill Master", systemImage: "flame.fill").foregroundStyle(ember).font(.caption)
                }
                DynamicIslandExpandedRegion(.trailing) { Text(context.state.temperatureLabel).font(.headline) }
                DynamicIslandExpandedRegion(.bottom) {
                    VStack(alignment: .leading, spacing: 4) {
                        Text(context.attributes.title).font(.headline)
                        HStack {
                            Text(context.isStale ? "Check your cook" : context.state.phase)
                            Spacer()
                            if !context.isStale {
                                Text(timerInterval: context.state.startedAt...context.state.endsAt, countsDown: true).monospacedDigit()
                            }
                        }.font(.caption)
                    }
                }
            } compactLeading: {
                Image(systemName: "flame.fill").foregroundStyle(ember)
            } compactTrailing: {
                if context.isStale {
                    Image(systemName: "checkmark")
                } else {
                    Text(timerInterval: context.state.startedAt...context.state.endsAt, countsDown: true)
                        .monospacedDigit().frame(maxWidth: 54)
                }
            } minimal: {
                Image(systemName: "flame.fill").foregroundStyle(ember)
            }
            .widgetURL(URL(string: "grillmaster://active"))
            .keylineTint(ember)
        }
    }
}

@main
struct GrillMasterWidgetBundle: WidgetBundle {
    var body: some Widget {
        GrillMasterCookWidget()
        GrillMasterLiveActivity()
    }
}
