import SwiftUI
import WebKit

final class GalaxyCoordinator: NSObject, WKNavigationDelegate, WKScriptMessageHandler {

    enum MessageName: String, CaseIterable {
        case nodeSelected, hapticFeedback, shareTable
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
        let av = UIActivityViewController(activityItems: [text], applicationActivities: nil)

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

    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
        impactLight.prepare()
        selection.prepare()
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.35) { [weak self] in
            self?.isLoaded.wrappedValue = true
        }
    }

    func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) {
        print("Galaxy load failed: \(error.localizedDescription)")
        isLoaded.wrappedValue = true
    }
}
