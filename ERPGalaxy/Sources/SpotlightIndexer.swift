import Foundation
import CoreSpotlight
import UniformTypeIdentifiers

/// Indexes the catalogue into Spotlight so "BSEG" typed into iOS search finds
/// the answer without opening the app. This is the offline-mobile advantage
/// made real — and a website cannot do it.
enum SpotlightIndexer {

    private static let domain = "com.daviddef.erpgalaxy.tables"
    private static let versionKey = "spotlight.indexed.build"

    /// Tied to the bundle version rather than a hand-bumped constant, because
    /// the constant was a step someone had to remember and the dataset changes
    /// every build.
    private static var version: String {
        (Bundle.main.infoDictionary?["CFBundleVersion"] as? String) ?? "0"
    }

    static func indexIfNeeded() {
        guard CSSearchableIndex.isIndexingAvailable() else { return }
        guard UserDefaults.standard.string(forKey: versionKey) != version else { return }

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
            let item = CSSearchableItem(uniqueIdentifier: t.id, domainIdentifier: domain, attributeSet: a)
            // Without this the default expiry is about a month. Combined with the
            // version gate below, the index was built once, silently expired, and
            // never rebuilt -- so anyone who had kept the app longer than that had
            // no Spotlight results at all. It is a catalogue, not news; it does
            // not go stale on a timer.
            item.expirationDate = .distantFuture
            return item
        }

        let index = CSSearchableIndex.default()
        index.deleteSearchableItems(withDomainIdentifiers: [domain]) { _ in
            // Batch: a single 2,000-item call is rejected on some devices.
            index.beginBatch()
            for chunk in stride(from: 0, to: items.count, by: 500).map({
                Array(items[$0..<min($0 + 500, items.count)])
            }) {
                index.indexSearchableItems(chunk)
            }
            // Only record success once the batch has actually landed. The old code
            // marked the index complete before any chunk returned, so a crash or a
            // backgrounding part-way through left it permanently half-built.
            index.endBatch(withClientState: Data(version.utf8)) { error in
                if let error {
                    print("Spotlight index error: \(error.localizedDescription)")
                    return
                }
                UserDefaults.standard.set(version, forKey: versionKey)
            }
        }
    }
}
