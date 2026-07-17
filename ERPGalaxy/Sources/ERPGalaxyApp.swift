import SwiftUI
import CoreSpotlight

@main
struct ERPGalaxyApp: App {
    @StateObject private var router = Router()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .preferredColorScheme(.dark)
                .environmentObject(router)
                .task { SpotlightIndexer.indexIfNeeded() }
                // Tapping a Spotlight result should land on that table, not just
                // open the app on the default view.
                .onContinueUserActivity(CSSearchableItemActionType) { activity in
                    if let id = activity.userInfo?[CSSearchableItemActivityIdentifier] as? String {
                        router.pending = id
                    }
                }
                // Widget tap: erpgalaxy://table/BSEG
                .onOpenURL { url in
                    guard url.scheme == "erpgalaxy", url.host == "table" else { return }
                    let id = url.lastPathComponent
                    if !id.isEmpty { router.pending = id }
                }
        }
    }
}

/// Carries a deep-link target from Spotlight to the WebView once it's loaded.
final class Router: ObservableObject {
    @Published var pending: String?
}
