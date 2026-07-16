# SAP Galaxy 🌌 — Claude Code Handover
## Xcode / iOS App Readiness

**Prepared for:** Claude Code CLI  
**Source artefact:** `/home/claude/sap-table-explorer.html`  
**Target:** Native Xcode project — `SAPGalaxy.xcodeproj`  
**Minimum iOS target:** iOS 15.0  
**Swift version:** Swift 5.9+

---

## 1. What You Are Building

**SAP Galaxy** is a data-practitioner reference tool for the SAP ECC6 → S/4HANA table universe. The existing HTML app contains:

| Dimension | Count |
|---|---|
| SAP tables (nodes) | 217 |
| Relationships (edges) | 567 |
| Modules covered | FI, CO, MM, SD, PP, HR, WM, PM, QM, PS, BASIS |
| Transaction code mappings | 80+ tables × multiple T-codes |
| T-code descriptions | 300+ |
| Field descriptions | 250+ ABAP field names |

The app renders as a **D3.js v7 force-directed galaxy graph** in a browser. It already has a mobile-responsive bottom-sheet overlay triggered at ≤700px viewport width.

---

## 2. Architecture Decision — WKWebView Wrapper (Recommended Fast Path)

### Why NOT a full SwiftUI rebuild (yet)
The D3.js force-directed graph simulation is 600+ lines of physics-based JavaScript. Reimplementing this natively in SwiftUI or Metal would be a significant undertaking (weeks of work, GPU rendering, custom gesture handling). The HTML file is already mobile-optimised.

### Recommended approach: WKWebView + Swift/SwiftUI shell

```
┌─────────────────────────────────────┐
│           SAPGalaxy iOS App          │
│                                      │
│  SwiftUI NavigationStack / TabView   │
│  ┌───────────────────────────────┐   │
│  │   GalaxyWebView (SwiftUI)     │   │
│  │   └─ WKWebView               │   │
│  │       └─ sap-galaxy.html     │   │  ← bundled in app
│  │           (184 KB, offline)   │   │
│  └───────────────────────────────┘   │
│                                      │
│  JS → Swift bridge (WKScriptMsg)     │
│  Swift → JS bridge (evaluateJS)      │
└─────────────────────────────────────┘
```

**Benefits:**
- Ship in days not weeks
- Zero data migration risk — all 217 tables/567 relationships already in HTML
- Dark mode already implemented
- Bottom-sheet overlay already implemented for mobile
- Future: extract SwiftUI panels one at a time alongside the WebView

---

## 3. Xcode Project Structure

```
SAPGalaxy/
├── SAPGalaxy.xcodeproj
├── SAPGalaxyApp.swift              ← @main entry point
├── ContentView.swift               ← root view (NavigationStack)
├── Views/
│   ├── GalaxyWebView.swift         ← WKWebView wrapper (UIViewRepresentable)
│   ├── GalaxyCoordinator.swift     ← WKNavigationDelegate + WKScriptMessageHandler
│   └── SplashView.swift            ← optional branded launch screen
├── Bridge/
│   ├── JSBridgeMessages.swift      ← Codable structs for JS→Swift messages
│   └── NativeActions.swift        ← haptics, share sheet, clipboard
├── Resources/
│   └── sap-galaxy.html             ← copy of sap-table-explorer.html (rename)
├── Assets.xcassets/
│   ├── AppIcon.appiconset/         ← galaxy/star icon
│   └── AccentColor.colorset/       ← #4f9cf9 (FI blue from MODULE_COLORS)
└── SAPGalaxy.entitlements
```

---

## 4. Swift Source Files — Complete Stubs

### `SAPGalaxyApp.swift`
```swift
import SwiftUI

@main
struct SAPGalaxyApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
                .preferredColorScheme(.dark)  // force dark — matches HTML theme
        }
    }
}
```

### `ContentView.swift`
```swift
import SwiftUI

struct ContentView: View {
    var body: some View {
        GalaxyWebView()
            .ignoresSafeArea()
            .statusBarHidden(false)
    }
}
```

### `Views/GalaxyWebView.swift`
```swift
import SwiftUI
import WebKit

struct GalaxyWebView: UIViewRepresentable {

    func makeCoordinator() -> GalaxyCoordinator {
        GalaxyCoordinator()
    }

    func makeUIView(context: Context) -> WKWebView {
        let config = WKWebViewConfiguration()

        // Register JS→Swift message handlers
        let contentController = WKUserContentController()
        contentController.add(context.coordinator, name: "nodeSelected")
        contentController.add(context.coordinator, name: "hapticFeedback")
        contentController.add(context.coordinator, name: "shareTable")
        config.userContentController = contentController

        // Allow local file access for bundled HTML
        config.preferences.javaScriptEnabled = true

        let webView = WKWebView(frame: .zero, configuration: config)
        webView.navigationDelegate = context.coordinator
        webView.scrollView.bounces = false
        webView.isOpaque = false
        webView.backgroundColor = UIColor(red: 0.04, green: 0.04, blue: 0.09, alpha: 1) // #0a0a17

        // Load bundled HTML file
        if let url = Bundle.main.url(forResource: "sap-galaxy", withExtension: "html") {
            webView.loadFileURL(url, allowingReadAccessTo: url.deletingLastPathComponent())
        }

        context.coordinator.webView = webView
        return webView
    }

    func updateUIView(_ uiView: WKWebView, context: Context) {
        // No dynamic updates needed — all state lives in JS
    }
}
```

### `Views/GalaxyCoordinator.swift`
```swift
import WebKit
import UIKit

class GalaxyCoordinator: NSObject, WKNavigationDelegate, WKScriptMessageHandler {

    weak var webView: WKWebView?

    // MARK: - WKScriptMessageHandler (JS → Swift)

    func userContentController(
        _ userContentController: WKUserContentController,
        didReceive message: WKScriptMessage
    ) {
        switch message.name {

        case "nodeSelected":
            // JS sends: { tableId: "BKPF", module: "FI" }
            if let body = message.body as? [String: String] {
                handleNodeSelected(tableId: body["tableId"] ?? "", module: body["module"] ?? "")
            }

        case "hapticFeedback":
            // JS sends: { style: "light" | "medium" | "heavy" | "selection" }
            if let body = message.body as? [String: String] {
                triggerHaptic(style: body["style"] ?? "light")
            }

        case "shareTable":
            // JS sends: { tableId: "BKPF", shortDesc: "Accounting Document Header" }
            if let body = message.body as? [String: String] {
                shareTable(tableId: body["tableId"] ?? "", desc: body["shortDesc"] ?? "")
            }

        default:
            break
        }
    }

    // MARK: - Actions

    private func handleNodeSelected(tableId: String, module: String) {
        triggerHaptic(style: "selection")
        // Could update a SwiftUI @Published var to show native overlays in future
    }

    private func triggerHaptic(style: String) {
        switch style {
        case "heavy":
            UIImpactFeedbackGenerator(style: .heavy).impactOccurred()
        case "medium":
            UIImpactFeedbackGenerator(style: .medium).impactOccurred()
        case "selection":
            UISelectionFeedbackGenerator().selectionChanged()
        default:
            UIImpactFeedbackGenerator(style: .light).impactOccurred()
        }
    }

    private func shareTable(tableId: String, desc: String) {
        let text = "SAP Table \(tableId): \(desc)\n\nExplored via SAP Galaxy 🌌"
        let av = UIActivityViewController(activityItems: [text], applicationActivities: nil)
        // Present from root view controller
        if let scene = UIApplication.shared.connectedScenes.first as? UIWindowScene,
           let root = scene.windows.first?.rootViewController {
            av.popoverPresentationController?.sourceView = root.view
            root.present(av, animated: true)
        }
    }

    // MARK: - Swift → JS (call these to control the web view)

    func focusTable(_ tableId: String) {
        let js = "enterFocus('\(tableId)');"
        webView?.evaluateJavaScript(js, completionHandler: nil)
    }

    func searchTable(_ query: String) {
        // Escape for JS string
        let escaped = query.replacingOccurrences(of: "'", with: "\\'")
        let js = """
        document.getElementById('search').value = '\(escaped)';
        document.getElementById('search').dispatchEvent(new Event('input'));
        """
        webView?.evaluateJavaScript(js, completionHandler: nil)
    }

    // MARK: - WKNavigationDelegate

    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
        // Inject JS bridge callbacks into the page after load
        injectBridgeCallbacks(webView)
    }

    private func injectBridgeCallbacks(_ webView: WKWebView) {
        // Wrap node tap to also fire haptic via native bridge
        let js = """
        (function() {
            // Intercept D3 node click to send haptic + nodeSelected events
            const _origNodeClick = window.__nodeClickCallback;
            window.__sapGalaxyNativeBridge = {
                onNodeTap: function(tableId, module) {
                    window.webkit.messageHandlers.hapticFeedback.postMessage({style: 'selection'});
                    window.webkit.messageHandlers.nodeSelected.postMessage({tableId: tableId, module: module});
                },
                onShare: function(tableId, shortDesc) {
                    window.webkit.messageHandlers.shareTable.postMessage({tableId: tableId, shortDesc: shortDesc});
                }
            };
        })();
        """
        webView.evaluateJavaScript(js, completionHandler: nil)
    }
}
```

---

## 5. HTML File Modifications Needed

After adding the HTML to the Xcode bundle, make these small JS additions inside `sap-galaxy.html`:

### 5a. Add native haptic on node tap
Find the D3 node click handler (search for `.on('click', function(event, d)`). Add inside the click handler:

```javascript
// Native iOS bridge (no-op in browser)
if (window.webkit?.messageHandlers?.hapticFeedback) {
    window.webkit.messageHandlers.hapticFeedback.postMessage({style: 'selection'});
}
```

### 5b. Add native Share button to sidebar/bottom-sheet
Inside `buildDetailHTML(d)`, add a share button to the returned `bodyHtml`:

```javascript
const shareBtn = window.webkit?.messageHandlers?.shareTable
    ? `<button class="focus-btn" onclick="
        window.webkit.messageHandlers.shareTable.postMessage(
          {tableId:'${d.id}', shortDesc:'${d.shortDesc.replace(/'/g,"\\'")}'}
        )">📤 Share Table</button>`
    : '';
// Append shareBtn to bodyHtml before return
```

### 5c. Viewport meta tag (verify it exists)
The HTML must have this in `<head>` — confirm it's present:
```html
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
```

### 5d. Safe area insets (iPhone notch / Dynamic Island)
Add this CSS to handle the notch:
```css
body {
    padding-top: env(safe-area-inset-top);
    padding-bottom: env(safe-area-inset-bottom);
}
#sidebar {
    padding-top: env(safe-area-inset-top);
}
```

---

## 6. Xcode Project Settings

| Setting | Value |
|---|---|
| Bundle Identifier | `com.yourname.sapgalaxy` |
| Display Name | SAP Galaxy |
| Version | 1.0.0 |
| Build | 1 |
| Minimum Deployments | iOS 15.0 |
| Device | iPhone + iPad (Universal) |
| Orientation | Portrait + Landscape |
| Appearance | Dark only (Info.plist: `UIUserInterfaceStyle = Dark`) |
| Status Bar Style | Light Content |

### Info.plist additions
```xml
<key>UIUserInterfaceStyle</key>
<string>Dark</string>
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsLocalNetworking</key>
    <true/>
</dict>
```

### App Icon
Use a dark background (#0a0a17) with a glowing star/galaxy cluster. The accent colour is `#4f9cf9` (FI module blue). Size requirements: 1024×1024 for App Store, plus all @1x/@2x/@3x sizes for iPhone/iPad.

---

## 7. Step-by-Step Build Instructions for Claude Code

```
1. Create new Xcode project
   File → New → Project → iOS → App
   Product Name: SAPGalaxy
   Interface: SwiftUI
   Language: Swift
   Bundle ID: com.[yourname].sapgalaxy

2. Add the HTML file
   - Drag /home/claude/sap-table-explorer.html into the Xcode project navigator
   - Rename to sap-galaxy.html
   - Target membership: ✅ SAPGalaxy
   - "Add to targets" dialog: Copy items if needed ✅

3. Replace ContentView.swift with the stub above

4. Create Views/ group and add:
   - GalaxyWebView.swift
   - GalaxyCoordinator.swift

5. Apply HTML modifications from Section 5 above

6. Set deployment target to iOS 15.0

7. Set UIUserInterfaceStyle = Dark in Info.plist

8. Add App Icon (1024×1024 minimum) to Assets.xcassets

9. Build & run on iPhone simulator (iPhone 15 Pro recommended)

10. Test checklist:
    ✅ Graph renders and animates
    ✅ Node tap shows bottom-sheet
    ✅ Module filter chips work
    ✅ ECC / S4 toggle works
    ✅ Search finds tables (try "BKPF", "BSEG" — should show ACDOCA)
    ✅ Focus mode (1-hop) works
    ✅ Lifecycle link colours correct (green=new S4, red dashed=ECC only, grey=retained)
    ✅ Haptic fires on node tap (real device only)
    ✅ Share sheet opens from Share button
    ✅ Landscape orientation supported
    ✅ No horizontal scroll bleed
```

---

## 8. Current Feature Inventory (HTML → iOS parity)

| Feature | HTML Status | iOS Action |
|---|---|---|
| D3.js force graph (217 nodes, 567 edges) | ✅ Complete | Auto via WKWebView |
| Module colour coding (11 modules) | ✅ Complete | Auto |
| ECC6 / S4HANA view toggle | ✅ Complete | Auto |
| Text search (id, desc, module, s4note) | ✅ Complete | Auto |
| 1-hop focus mode | ✅ Complete | Auto |
| Lifecycle link colours (green/red dashed/grey) | ✅ Complete | Auto |
| ECC→S/4 journey diagram in sidebar | ✅ Complete | Auto |
| Key fields with human descriptions | ✅ Complete | Auto |
| SAP T-code chips with descriptions | ✅ Complete | Auto |
| Mobile bottom-sheet overlay (≤700px) | ✅ Complete | Auto (WKWebView viewport = iPhone width) |
| Haptic feedback on node tap | ❌ Not in HTML | Add per Section 5a |
| Native share sheet | ❌ Not in HTML | Add per Section 5b |
| Native search bar (UISearchBar) | ❌ Optional | Future: evaluateJS bridge |
| Spotlight / Core Spotlight indexing | ❌ Optional | Future: index 217 tables |
| Offline support | ✅ All data in HTML | Auto — no network calls |
| Dark mode | ✅ Only mode | Auto |

---

## 9. Known Issues & Gotchas

**Issue:** `WKWebView` blocks `file://` cross-origin requests by default.  
**Fix:** Use `loadFileURL(_:allowingReadAccessTo:)` (already in the stub above) — this is required for loading local HTML with relative paths.

**Issue:** WKWebView `bounces` may feel wrong for a graph.  
**Fix:** `webView.scrollView.bounces = false` (already in stub).

**Issue:** The graph's SVG `<defs>` arrow markers have IDs `arrow`, `arrow-new`, `arrow-ecc`. These must be unique per-page — not an issue since it's a single HTML file.

**Issue:** Pinch-to-zoom will zoom the whole WebView, not just the D3 canvas.  
**Fix:** D3 already handles its own zoom via `d3.zoom()`. Disable WKWebView native zoom:
```swift
webView.scrollView.minimumZoomScale = 1.0
webView.scrollView.maximumZoomScale = 1.0
```

**Issue:** On first launch the graph takes ~300ms to render (D3 simulation settles).  
**Fix:** Consider a branded splash/loading overlay (see `SplashView.swift` stub slot).

---

## 10. Future Roadmap (Post-Launch)

Once the WKWebView version ships, individual panels can be extracted to native SwiftUI:

1. **Table Detail Sheet** → SwiftUI `Sheet` with `List` of key fields, T-codes, relationships — replaces the HTML bottom-sheet
2. **Module Filter** → SwiftUI toolbar `Menu` with toggle buttons
3. **Search** → SwiftUI `searchable()` modifier, bridge to D3 via `evaluateJavaScript`
4. **Core Data / SwiftData** → Migrate the 217-table JSON array into a local database for Spotlight, Siri Shortcuts, and Widget support
5. **Widget** → "Table of the Day" widget showing a random SAP table fact
6. **Siri Shortcut** → "Hey Siri, look up SAP table BKPF"

---

## 11. Source File Reference

```
/home/claude/sap-table-explorer.html
  Size:      ~184 KB
  Lines:     ~2,500
  Tables:    217 (TABLES array)
  Links:     567 (LINKS_RAW array)
  D3:        v7 from cdnjs.cloudflare.com
  Self-contained: YES (no external data calls, no backend)
  
Key JS globals to know:
  TABLES[]          — 217 table objects
  LINKS_RAW[]       — 567 [fromId, toId] pairs
  MODULE_COLORS{}   — 11 module → hex colour
  FIELD_DESC{}      — 250+ ABAP field → English description
  TCODE_MAP{}       — table → T-code array
  TCODE_DESC{}      — T-code → English description
  LINK_COLORS{}     — lifecycle → hex colour

Key JS functions:
  getVisibleTables()         — filtered table list (respects focus, view, search)
  buildDetailHTML(d)         — sidebar/sheet HTML for a table node
  buildJourney()             — ECC→S/4 journey flow diagram
  linkLifecycle(a, b)        — 'new_s4' | 'ecc_only' | 'retained'
  getFocusNeighbours(id)     — Set of center + 1-hop neighbour IDs
  enterFocus(id) / exitFocus()
  openMobilePanel(id) / closeMobilePanel()
  fieldLabel(f)              — HTML chip for a key field
  tcodeLabel(tc)             — HTML chip for a T-code
```

---

## 12. Contact / Context

This handover was prepared from a Cowork (Claude) session. The HTML source is the single deliverable artefact. All data is embedded — there is no server, no API, no database to migrate.

The intended user of the app is an **SAP data practitioner** (functional consultant, data architect, developer) who needs quick offline reference for SAP table structures and ECC→S/4HANA migration mappings.

Design language: dark space/galaxy theme, glowing nodes, module colour coding. Tone: "idiot's guide" accessible, not enterprise-dry.

---

*End of handover document. Good luck with the Xcode build! 🚀*
