import WidgetKit
import SwiftUI

struct TableEntry: TimelineEntry {
    let date: Date
    let table: SAPTable?
}

struct TableProvider: TimelineProvider {
    func placeholder(in context: Context) -> TableEntry {
        TableEntry(date: Date(), table: TableStore.tableOfTheDay())
    }
    func getSnapshot(in context: Context, completion: @escaping (TableEntry) -> Void) {
        completion(TableEntry(date: Date(), table: TableStore.tableOfTheDay()))
    }
    func getTimeline(in context: Context, completion: @escaping (Timeline<TableEntry>) -> Void) {
        let now = Date()
        let cal = Calendar.current
        // Refresh at the next midnight — the table is keyed to the day.
        let next = cal.startOfDay(for: cal.date(byAdding: .day, value: 1, to: now) ?? now)
        completion(Timeline(entries: [TableEntry(date: now, table: TableStore.tableOfTheDay(for: now))],
                            policy: .after(next)))
    }
}

private func moduleColor(_ m: String) -> Color {
    switch m {
    case "FI": return Color(red: 0.31, green: 0.61, blue: 0.98)
    case "CO": return Color(red: 0.65, green: 0.55, blue: 0.98)
    case "MM": return Color(red: 0.20, green: 0.83, blue: 0.60)
    case "SD": return Color(red: 0.98, green: 0.57, blue: 0.24)
    case "PP": return Color(red: 0.98, green: 0.75, blue: 0.14)
    case "HR": return Color(red: 0.96, green: 0.45, blue: 0.71)
    case "WM": return Color(red: 0.18, green: 0.83, blue: 0.75)
    case "PM": return Color(red: 0.97, green: 0.44, blue: 0.44)
    case "QM": return Color(red: 0.64, green: 0.90, blue: 0.21)
    case "PS": return Color(red: 0.51, green: 0.55, blue: 0.97)
    case "EHS": return Color(red: 0.08, green: 0.72, blue: 0.65)
    case "FM": return Color(red: 0.75, green: 0.52, blue: 0.99)
    default: return Color(red: 0.58, green: 0.64, blue: 0.72)
    }
}

private func fateStyle(_ fate: String) -> (String, Color)? {
    // Order matters: "Compatibility view" must be tested before anything that
    // could also match it. These mirror the icons the web app uses, so the same
    // outcome looks the same wherever you meet it.
    if fate.contains("Disappears")         { return ("❌", Color(red: 0.94, green: 0.27, blue: 0.27)) }
    if fate.contains("Compatibility view") { return ("🪞", Color(red: 0.31, green: 0.61, blue: 0.98)) }
    if fate.contains("Replaced")           { return ("➡️", Color(red: 0.96, green: 0.62, blue: 0.04)) }
    if fate.contains("Changes")            { return ("⚠️", Color(red: 0.96, green: 0.62, blue: 0.04)) }
    if fate.contains("New")                { return ("🆕", Color(red: 0.13, green: 0.77, blue: 0.37)) }
    if fate.contains("Unchanged")          { return ("✅", Color(red: 0.13, green: 0.77, blue: 0.37)) }
    if fate.contains("Carries")            { return ("✅", Color(red: 0.13, green: 0.77, blue: 0.37)) }
    return nil
}

struct TableOfTheDayView: View {
    @Environment(\.widgetFamily) var family
    let entry: TableEntry

    var body: some View {
        if let t = entry.table {
            VStack(alignment: .leading, spacing: 5) {
                HStack(spacing: 5) {
                    Text("🌌").font(.caption2)
                    Text("TABLE OF THE DAY")
                        .font(.system(size: 8, weight: .bold)).kerning(0.6)
                        .foregroundStyle(.secondary)
                    Spacer()
                    Text(t.module)
                        .font(.system(size: 8, weight: .bold))
                        .padding(.horizontal, 5).padding(.vertical, 2)
                        .background(moduleColor(t.module).opacity(0.18), in: Capsule())
                        .foregroundStyle(moduleColor(t.module))
                }
                Text(t.id)
                    .font(.system(size: family == .systemSmall ? 20 : 26,
                                  weight: .bold, design: .monospaced))
                    .foregroundStyle(moduleColor(t.module))
                    .minimumScaleFactor(0.6).lineLimit(1)
                Text(t.desc)
                    .font(.system(size: family == .systemSmall ? 9 : 11))
                    .foregroundStyle(.secondary)
                    .lineLimit(family == .systemSmall ? 3 : 4)
                Spacer(minLength: 0)
                if let (icon, col) = fateStyle(t.fate) {
                    Text("\(icon) \(t.fate)")
                        .font(.system(size: 8, weight: .semibold))
                        .foregroundStyle(col).lineLimit(1).minimumScaleFactor(0.7)
                }
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
            .widgetURL(URL(string: "erpgalaxy://table/\(t.id)"))
        } else {
            Text("ERP Galaxy").font(.caption).foregroundStyle(.secondary)
        }
    }
}

struct TableOfTheDayWidget: Widget {
    var body: some WidgetConfiguration {
        StaticConfiguration(kind: "TableOfTheDay", provider: TableProvider()) { entry in
            TableOfTheDayView(entry: entry)
                .containerBackground(for: .widget) {
                    Color(red: 0.051, green: 0.067, blue: 0.09)
                }
        }
        .configurationDisplayName("Table of the Day")
        .description("One SAP table a day, in plain English, with its S/4HANA fate.")
        .supportedFamilies([.systemSmall, .systemMedium])
    }
}

@main
struct ERPGalaxyWidgetBundle: WidgetBundle {
    var body: some Widget { TableOfTheDayWidget() }
}
