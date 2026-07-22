import SwiftUI
import WebKit

final class GalaxyCoordinator: NSObject, WKNavigationDelegate, WKScriptMessageHandler {

    enum MessageName: String, CaseIterable {
        case nodeSelected, hapticFeedback, shareTable, exportTodo
    }

    weak var webView: WKWebView?
    private var isLoaded: Binding<Bool>

    private let impactLight  = UIImpactFeedbackGenerator(style: .light)
    private let impactMedium = UIImpactFeedbackGenerator(style: .medium)
    private let impactHeavy  = UIImpactFeedbackGenerator(style: .heavy)
    private let selection    = UISelectionFeedbackGenerator()

    init(isLoaded: Binding<Bool>) {
        self.isLoaded = isLoaded
        super.init()
    }

    // MARK: - JS → Swift

    func userContentController(_ controller: WKUserContentController,
                               didReceive message: WKScriptMessage) {
        guard let name = MessageName(rawValue: message.name) else { return }
        let body = message.body as? [String: String] ?? [:]

        switch name {
        case .nodeSelected:
            selection.selectionChanged()
        case .hapticFeedback:
            triggerHaptic(style: body["style"] ?? "light")
        case .shareTable:
            shareTable(tableId: body["tableId"] ?? "", desc: body["shortDesc"] ?? "")
        case .exportTodo:
            exportTodo(format: body["format"] ?? "share",
                       text: body["text"] ?? "",
                       html: body["html"] ?? "")
        }
    }

    private func triggerHaptic(style: String) {
        switch style {
        case "heavy":     impactHeavy.impactOccurred()
        case "medium":    impactMedium.impactOccurred()
        case "selection": selection.selectionChanged()
        default:          impactLight.impactOccurred()
        }
    }

    private func shareTable(tableId: String, desc: String) {
        guard !tableId.isEmpty else { return }
        let text = "SAP Table \(tableId): \(desc)\n\nExplored via ERP Galaxy 🌌"
        present(activityItems: [text])
    }

    /// The to-do list leaves the device only here, and only when the user taps
    /// share or export. `share` hands over plain text (Mail is in the sheet, so
    /// this covers emailing the list); `pdf` renders a paginated document first.
    private func exportTodo(format: String, text: String, html: String) {
        guard !text.isEmpty else { return }
        if format == "pdf", let url = writePDF(html: html) {
            present(activityItems: [url])
        } else {
            present(activityItems: [text])
        }
    }

    /// Paginated PDF via UIMarkupTextPrintFormatter — no offscreen WKWebView and
    /// no async load to race against, which matters because the share sheet has
    /// to be presented in the same user-initiated moment.
    private func writePDF(html: String) -> URL? {
        let formatter = UIMarkupTextPrintFormatter(markupText: html)
        let renderer = UIPrintPageRenderer()
        renderer.addPrintFormatter(formatter, startingAtPageAt: 0)

        // A4 at 72dpi with a 36pt (half-inch) margin.
        let page = CGRect(x: 0, y: 0, width: 595.2, height: 841.8)
        renderer.setValue(page, forKey: "paperRect")
        renderer.setValue(page.insetBy(dx: 36, dy: 36), forKey: "printableRect")

        let data = NSMutableData()
        UIGraphicsBeginPDFContextToData(data, page, nil)
        // numberOfPages triggers layout, so it must be read after the rects are set.
        let pages = renderer.numberOfPages
        guard pages > 0 else { UIGraphicsEndPDFContext(); return nil }
        for i in 0..<pages {
            UIGraphicsBeginPDFPage()
            renderer.drawPage(at: i, in: UIGraphicsGetPDFContextBounds())
        }
        UIGraphicsEndPDFContext()

        let url = FileManager.default.temporaryDirectory
            .appendingPathComponent("ERP Galaxy to-do.pdf")
        do {
            try data.write(to: url, options: .atomic)
            return url
        } catch {
            print("PDF write failed: \(error.localizedDescription)")
            return nil
        }
    }

    private func present(activityItems: [Any]) {
        let av = UIActivityViewController(activityItems: activityItems,
                                          applicationActivities: nil)

        // Resolve the *key* window of the active scene. `windows.first` on an
        // arbitrary scene breaks on iPad multi-window and Designed-for-iPad on Mac.
        guard let scene = UIApplication.shared.connectedScenes
                .compactMap({ $0 as? UIWindowScene })
                .first(where: { $0.activationState == .foregroundActive }),
              let root = scene.windows.first(where: { $0.isKeyWindow })?.rootViewController
        else { return }

        // Required on iPad/Mac or this traps.
        if let pop = av.popoverPresentationController {
            pop.sourceView = root.view
            pop.sourceRect = CGRect(x: root.view.bounds.midX, y: root.view.bounds.midY,
                                    width: 0, height: 0)
            pop.permittedArrowDirections = []
        }
        root.present(av, animated: true)
    }

    // MARK: - Swift → JS

    func focusTable(_ tableId: String) {
        evaluate("enterFocus(\(jsString(tableId)));")
    }

    /// Open a table from a Spotlight result: graph node if we have one,
    /// otherwise the Codex sheet.
    func showTable(_ id: String) {
        evaluate("""
        (function(){
          var id = \(jsString(id));
          if (typeof TABLES !== 'undefined' && TABLES.some(function(t){return t.id===id;})) { jumpTo(id); }
          else if (typeof CODEX !== 'undefined' && CODEX[id]) { openCodex(id); }
        })();
        """)
    }

    func search(_ query: String) {
        evaluate("""
        (function(){
          var el = document.getElementById('search');
          if (!el) return;
          el.value = \(jsString(query));
          el.dispatchEvent(new Event('input'));
        })();
        """)
    }

    private func evaluate(_ js: String) {
        webView?.evaluateJavaScript(js) { _, error in
            if let error { print("JS bridge error: \(error.localizedDescription)") }
        }
    }

    /// JSON-encode so quotes/backslashes/newlines can't break out of the literal.
    private func jsString(_ s: String) -> String {
        (try? String(data: JSONEncoder().encode(s), encoding: .utf8)) ?? "\"\""
    }

    // MARK: - Navigation

    /// 0.35s covers the D3 force simulation settling; the rest is deliberate.
    /// The bundled HTML loads fast enough that the splash was gone before the
    /// orbits had moved, so it held for a blink and read as a flash of dark.
    private static let splashSettle: TimeInterval = 0.35
    private static let splashLinger: TimeInterval = 1.0

    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
        impactLight.prepare()
        selection.prepare()
        let delay = Self.splashSettle + Self.splashLinger
        DispatchQueue.main.asyncAfter(deadline: .now() + delay) { [weak self] in
            self?.isLoaded.wrappedValue = true
        }
    }

    func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) {
        print("Galaxy load failed: \(error.localizedDescription)")
        isLoaded.wrappedValue = true
    }
}
