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

    /// Computed at build time by tools/build_native.py, using the same
    /// precedence as tableFate() in the web app: SAP's published verdict
    /// outranks our coarse ecc/s4 flags.
    ///
    /// This used to be re-derived here from the flags alone, which is why
    /// Spotlight told people BSIS "Disappears in S/4HANA" when SAP says it
    /// survives as a compatibility view and their reports keep working. Twenty
    /// tables were wrong. A rule stated in two places drifts; now it is stated
    /// once and Swift reads the answer.
    let fate: String
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
