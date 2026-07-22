import Foundation
import CoreSpotlight
import UniformTypeIdentifiers

/// Indexes the catalogue into Spotlight so "BSEG" typed into iOS search finds
/// the answer without opening the app. This is the offline-mobile advantage
/// made real — and a website cannot do it.
enum SpotlightIndexer {

    private static let domain = "com.daviddef.erpgalaxy.tables"
    private static let versionKey = "spotlight.indexed.build"

    /// All state is touched only on this queue, which is also what makes the
    /// re-entrancy guard below sound.
    private static let queue = DispatchQueue(label: "com.daviddef.erpgalaxy.spotlight")
    private static var isIndexing = false

    /// Tied to the bundle version rather than a hand-bumped constant, because
    /// the constant was a step someone had to remember and the dataset changes
    /// every build.
    private static var version: String {
        (Bundle.main.infoDictionary?["CFBundleVersion"] as? String) ?? "0"
    }

    static func indexIfNeeded() {
        guard CSSearchableIndex.isIndexingAvailable() else { return }

        // Off the main thread: building 2,273 attribute sets is real work, and
        // this is called from .task during launch.
        queue.async {
            // The version gate alone is not enough to stop a second run. It is
            // only closed once indexing finishes, which takes seconds, and
            // .task can fire more than once — a changed view identity, a
            // reconnected scene, or a second scene on iPad and Mac. Build 27
            // crashed on exactly that: two runs overlapped and CoreSpotlight
            // raised an exception. This guard closes the window immediately.
            guard !isIndexing else { return }
            guard UserDefaults.standard.string(forKey: versionKey) != version else { return }
            isIndexing = true

            let items = TableStore.all.map { t -> CSSearchableItem in
                let a = CSSearchableItemAttributeSet(contentType: UTType.text)
                a.title = t.id
                let fate = t.fate
                // Spotlight collapses the description to one line, so a newline here
            // rendered as "Material Document Line Items (ECC) Disappears in
            // S/4HANA" -- a run-on sentence. A separator keeps the two facts
            // visibly separate.
            a.contentDescription = fate.isEmpty ? t.desc : "\(t.desc) · \(fate)"
                // Let people find a table by module or plain words, not just its id.
                a.keywords = [t.id, t.module, "SAP", "table"] + t.desc
                    .split(whereSeparator: { !$0.isLetter && !$0.isNumber })
                    .filter { $0.count > 3 }
                    .prefix(8)
                    .map(String.init)
                a.displayName = "\(t.id) — \(t.module)"
                let item = CSSearchableItem(uniqueIdentifier: t.id, domainIdentifier: domain, attributeSet: a)
                // Without this the default expiry is about a month. Combined with
                // the version gate, the index was built once, silently expired,
                // and never rebuilt — so anyone who had kept the app longer than
                // that had no Spotlight results at all. It is a catalogue, not
                // news; it does not go stale on a timer.
                item.expirationDate = .distantFuture
                return item
            }

            let chunks = stride(from: 0, to: items.count, by: 500).map {
                Array(items[$0..<min($0 + 500, items.count)])
            }

            let index = CSSearchableIndex.default()
            index.deleteSearchableItems(withDomainIdentifiers: [domain]) { _ in
                // Deliberately NOT beginBatch/endBatch. That pairing is what
                // crashed build 27: beginBatch throws if a batch is already open,
                // and it bought nothing here. Per-chunk completions give the same
                // guarantee — only record success once every chunk has landed —
                // with no exception to trip over.
                let group = DispatchGroup()
                var failed = false
                for chunk in chunks {
                    group.enter()
                    index.indexSearchableItems(chunk) { error in
                        if let error {
                            failed = true
                            print("Spotlight index error: \(error.localizedDescription)")
                        }
                        group.leave()
                    }
                }
                group.notify(queue: queue) {
                    // A partial index must not be recorded as complete, or it
                    // never gets rebuilt.
                    if !failed {
                        UserDefaults.standard.set(version, forKey: versionKey)
                    }
                    isIndexing = false
                }
            }
        }
    }
}
