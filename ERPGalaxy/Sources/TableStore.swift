import Foundation

/// The catalogue, available to native Swift — the widget and Spotlight can't
/// reach inside the WebView's JS, so the same data ships as JSON alongside it.
struct SAPTable: Codable, Identifiable, Hashable {
    let id: String
    let module: String
    let desc: String
    let tier: Int
    let s4status: String?
    let ecc: Bool?
    let s4: Bool?

    /// Mirrors tableFate() in the web app: flags first, but SAP's published
    /// verdict outranks them (a compatibility view is not "gone").
    var fate: String {
        if ecc == false && s4 == true { return "New in S/4HANA" }
        if ecc == true && s4 == false { return "Disappears in S/4HANA" }
        switch s4status {
        case "deprecated": return "Disappears in S/4HANA"
        case "modified":   return "Changes in S/4HANA"
        case "new":        return "New in S/4HANA"
        default:           return tier == 1 ? "Carries over to S/4HANA" : ""
        }
    }
}

enum TableStore {
    static let all: [SAPTable] = {
        guard let url = Bundle.main.url(forResource: "tables_native", withExtension: "json",
                                        subdirectory: "Data")
                ?? Bundle.main.url(forResource: "tables_native", withExtension: "json"),
              let data = try? Data(contentsOf: url),
              let rows = try? JSONDecoder().decode([SAPTable].self, from: data)
        else {
            assertionFailure("tables_native.json missing from bundle")
            return []
        }
        return rows
    }()

    static func find(_ id: String) -> SAPTable? {
        all.first { $0.id.caseInsensitiveCompare(id) == .orderedSame }
    }

    /// Curated tables first — they have real explanations, so they make a
    /// better "table of the day" than a config stub.
    static func tableOfTheDay(for date: Date = Date()) -> SAPTable? {
        let pool = all.filter { $0.tier == 1 && !$0.desc.isEmpty }
        guard !pool.isEmpty else { return all.first }
        let day = Calendar(identifier: .gregorian)
            .ordinality(of: .day, in: .era, for: date) ?? 0
        return pool[day % pool.count]
    }
}
