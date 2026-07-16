import SwiftUI

/// Covers the ~300ms while the D3 force simulation settles, so first launch
/// doesn't show a graph visibly jittering into place.
struct SplashView: View {
    @State private var pulse = false

    var body: some View {
        VStack(spacing: 14) {
            Text("🌌")
                .font(.system(size: 56))
                .scaleEffect(pulse ? 1.06 : 0.94)
                .animation(.easeInOut(duration: 1.1).repeatForever(autoreverses: true), value: pulse)
            Text("SAP Galaxy")
                .font(.title2.weight(.bold))
                .foregroundStyle(
                    LinearGradient(colors: [Color(red: 0.31, green: 0.61, blue: 0.98),
                                            Color(red: 0.65, green: 0.55, blue: 0.98)],
                                   startPoint: .leading, endPoint: .trailing)
                )
            Text("Mapping the table universe…")
                .font(.footnote)
                .foregroundStyle(.secondary)
        }
        .onAppear { pulse = true }
    }
}
