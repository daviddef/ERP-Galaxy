import SwiftUI
import WebKit

struct GalaxyWebView: UIViewRepresentable {
    @Binding var isLoaded: Bool

    func makeCoordinator() -> GalaxyCoordinator {
        GalaxyCoordinator(isLoaded: $isLoaded)
    }

    func makeUIView(context: Context) -> WKWebView {
        let config = WKWebViewConfiguration()

        let controller = WKUserContentController()
        for name in GalaxyCoordinator.MessageName.allCases {
            controller.add(context.coordinator, name: name.rawValue)
        }
        config.userContentController = controller

        // `preferences.javaScriptEnabled` is deprecated since iOS 14.
        config.defaultWebpagePreferences.allowsContentJavaScript = true

        let webView = WKWebView(frame: .zero, configuration: config)
        webView.navigationDelegate = context.coordinator
        webView.scrollView.bounces = false
        webView.isOpaque = false
        webView.backgroundColor = UIColor(red: 0.051, green: 0.067, blue: 0.09, alpha: 1)
        webView.scrollView.contentInsetAdjustmentBehavior = .never

        // D3 handles its own pan/zoom via d3.zoom(); let the WebView's zoom
        // stay out of the way rather than fighting it.
        webView.scrollView.minimumZoomScale = 1
        webView.scrollView.maximumZoomScale = 1

        // loadFileURL(_:allowingReadAccessTo:) with the *directory* is what lets
        // the page reach vendor/d3.min.js under file://.
        if let url = Bundle.main.url(forResource: "sap-galaxy", withExtension: "html", subdirectory: "Web") {
            webView.loadFileURL(url, allowingReadAccessTo: url.deletingLastPathComponent())
        } else {
            assertionFailure("sap-galaxy.html missing from bundle — check the Web folder reference")
        }

        context.coordinator.webView = webView
        return webView
    }

    func updateUIView(_ uiView: WKWebView, context: Context) {
        // All graph state lives in JS; nothing to push from SwiftUI yet.
    }
}
