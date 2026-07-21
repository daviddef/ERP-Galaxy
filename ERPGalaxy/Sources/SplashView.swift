import SwiftUI

/// Covers the moment while the D3 force simulation settles, so first launch
/// doesn't show a graph visibly jittering into place.
///
/// Three real tables orbit the galaxy in their module colours — the same
/// palette the graph uses, so the splash is a preview of the thing rather than
/// unrelated decoration. Positions come from a TimelineView clock rather than a
/// rotationEffect, which keeps the labels upright instead of tumbling.
struct SplashView: View {

    private struct Planet {
        let id: String
        let colour: Color
        let radius: CGFloat
        let speed: Double      // radians per second
        let phase: Double
    }

    // Module colours, matched to MODULE_COLORS in the web app.
    private static let fi = Color(red: 0.31,  green: 0.61,  blue: 0.98)
    private static let mm = Color(red: 0.204, green: 0.827, blue: 0.600)
    private static let sd = Color(red: 0.984, green: 0.573, blue: 0.235)

    private static let planets: [Planet] = [
        Planet(id: "BSEG", colour: fi, radius: 62,  speed: 0.55, phase: 0),
        Planet(id: "MARA", colour: mm, radius: 96,  speed: 0.38, phase: 2.1),
        Planet(id: "VBAK", colour: sd, radius: 124, speed: 0.27, phase: 4.0),
    ]

    /// One is picked per launch — the splash is too brief to rotate through
    /// them, but you get a different one each time you open the app.
    /// Each is either a plain joke or something the app actually holds:
    /// MKPF really does move to MATDOC, and the material number really did go
    /// to 40 characters. Nothing here asserts an SAP fact that isn't true.
    private static let lines = [
        "Mapping the table universe…",
        "Warming up 2,001 tables…",
        "Politely ignoring your Z-tables…",
        "Checking MKPF's forwarding address…",
        "Working out what survives 2027…",
        "Counting the compatibility views…",
        "Finding where the material number went…",
        "Wondering why it's always BSEG…",
        "Drawing 411 relationships…",
        "Asking MARA where it keeps its plants…",
    ]

    @State private var pulse = false
    @State private var line = SplashView.lines.randomElement() ?? "Mapping the table universe…"

    var body: some View {
        VStack(spacing: 18) {
            TimelineView(.animation) { context in
                let t = context.date.timeIntervalSinceReferenceDate
                ZStack {
                    ForEach(SplashView.planets.indices, id: \.self) { i in
                        orbitPath(for: SplashView.planets[i])
                    }
                    ForEach(SplashView.planets.indices, id: \.self) { i in
                        planetChip(SplashView.planets[i], at: t)
                    }
                    galacticCore
                }
                .frame(width: 340, height: 156)
            }

            Text("🌌 ERP Galaxy")
                .font(.title2.weight(.bold))
                .foregroundStyle(
                    LinearGradient(colors: [Self.fi, Color(red: 0.65, green: 0.55, blue: 0.98)],
                                   startPoint: .leading, endPoint: .trailing)
                )

            Text(line)
                .font(.footnote)
                .foregroundStyle(.secondary)
                .transition(.opacity)
        }
        .onAppear { pulse = true }
        .accessibilityElement(children: .ignore)
        .accessibilityLabel("ERP Galaxy. \(line)")
    }

    /// A glowing core rather than the 🌌 glyph: Apple draws Milky Way as a
    /// framed photograph, which at this size reads as a white box rather than a
    /// galaxy. The emoji still leads the wordmark, matching the web header.
    private var galacticCore: some View {
        ZStack {
            Circle()
                .fill(RadialGradient(colors: [Color.white.opacity(0.22),
                                              Self.fi.opacity(0.16),
                                              Color.clear],
                                     center: .center, startRadius: 2, endRadius: 46))
                .frame(width: 92, height: 92)
            Circle()
                .fill(RadialGradient(colors: [Color.white,
                                              Color(red: 0.72, green: 0.84, blue: 1.0),
                                              Self.fi],
                                     center: .init(x: 0.38, y: 0.34),
                                     startRadius: 1, endRadius: 22))
                .frame(width: 34, height: 34)
                .shadow(color: Self.fi.opacity(0.8), radius: 14)
        }
        .scaleEffect(pulse ? 1.07 : 0.93)
        .animation(.easeInOut(duration: 1.6).repeatForever(autoreverses: true), value: pulse)
    }

    /// The orbit each planet travels, squashed vertically so the group reads as
    /// a plane seen at an angle rather than concentric circles.
    private func orbitPath(for p: Planet) -> some View {
        Ellipse()
            .strokeBorder(Color.white.opacity(0.06), lineWidth: 1)
            .frame(width: p.radius * 2, height: p.radius * 2 * Self.squash)
    }

    private static let squash: CGFloat = 0.42

    private func planetChip(_ p: Planet, at t: TimeInterval) -> some View {
        let angle = t * p.speed + p.phase
        let x = cos(angle) * p.radius
        let y = sin(angle) * p.radius * Self.squash
        // sin(angle) > 0 puts the planet on the near side of the orbit; lift it
        // slightly so the ring reads as 3D rather than flat.
        let near = (sin(angle) + 1) / 2
        return Text(p.id)
            .font(.system(size: 10, weight: .heavy, design: .monospaced))
            .foregroundStyle(Color(red: 0.051, green: 0.067, blue: 0.09))
            .padding(.horizontal, 6)
            .padding(.vertical, 3)
            .background(Capsule().fill(p.colour))
            .shadow(color: p.colour.opacity(0.5), radius: 6)
            .scaleEffect(0.86 + 0.14 * near)
            .opacity(0.55 + 0.45 * near)
            .offset(x: x, y: y)
    }
}
