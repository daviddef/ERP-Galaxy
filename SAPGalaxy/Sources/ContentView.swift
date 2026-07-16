import SwiftUI

struct ContentView: View {
    @State private var isLoaded = false

    var body: some View {
        ZStack {
            Color(red: 0.051, green: 0.067, blue: 0.09).ignoresSafeArea() // #0d1117
            GalaxyWebView(isLoaded: $isLoaded)
                .ignoresSafeArea()
                .opacity(isLoaded ? 1 : 0)
            if !isLoaded {
                SplashView()
            }
        }
        .animation(.easeInOut(duration: 0.35), value: isLoaded)
    }
}
