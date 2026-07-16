import Foundation
import CoreSpotlight
import UniformTypeIdentifiers

/// Indexes the catalogue into Spotlight so "BSEG" typed into iOS search finds
/// the answer without opening the app. This is the offline-mobile advantage
/// made real — and a website cannot do it.
enum SpotlightIndexer {

    private static let domain = "com.daviddef.erpgalaxy.tables"
    private static let versionKey = "spotlight.indexed.version"
    /// Bump when the dataset or the attribute shape changes.
    private static let version = 3

    static func indexIfNeeded() {
        guard CSSearchableIndex.isIndexingAvailable() else { return }
        guard UserDefaults.standard.integer(forKey: versionKey) != version else { return }

        let items = TableStore.all.map { t -> CSSearchableItem in
            let a = CSSearchableItemAttributeSet(contentType: UTType.text)
            a.title = t.id
            let fate = t.fate
            a.contentDescription = fate.isEmpty ? t.desc : "\(t.desc)\n\(fate)"
            // Let people find a table by module or plain words, not just its id.
            a.keywords = [t.id, t.module, "SAP", "table"] + t.desc
                .split(whereSeparator: { !$0.isLetter && !$0.isNumber })
                .filter { $0.count > 3 }
                .prefix(8)
                .map(String.init)
            a.displayName = "\(t.id) — \(t.module)"
            return CSSearchableItem(uniqueIdentifier: t.id, domainIdentifier: domain, attributeSet: a)
        }

        let index = CSSearchableIndex.default()
        index.deleteSearchableItems(withDomainIdentifiers: [domain]) { _ in
            // Batch: a single 2,000-item call is rejected on some devices.
            for chunk in stride(from: 0, to: items.count, by: 500).map({
                Array(items[$0..<min($0 + 500, items.count)])
            }) {
                index.indexSearchableItems(chunk) { error in
                    if let error { print("Spotlight index error: \(error.localizedDescription)") }
                }
            }
            UserDefaults.standard.set(version, forKey: versionKey)
        }
    }
}
