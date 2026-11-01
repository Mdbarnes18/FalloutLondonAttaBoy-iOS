import SwiftUI

struct AttaBoyBootView: View {
    let onComplete: () -> Void
    @State private var phase = 0
    @State private var scanlineOffset: CGFloat = -24

    private let messages = [
        "ATTA-BOY PERSONAL INFORMATION PROCESSOR",
        "DISPLAY INITIALIZING...",
        "MEMORY CHECK ................. OK",
        "SYSTEM LINK .................. STANDBY",
        "FALLOUT: LONDON DATABASE ..... READY",
        "SYSTEM READY\n\nWITH THANKS TO TEAM FOLON"
    ]

    var body: some View {
        ZStack {
            PipTheme.background.ignoresSafeArea()

            RoundedRectangle(cornerRadius: 22)
                .fill(PipTheme.panel)
                .overlay {
                    RoundedRectangle(cornerRadius: 22)
                        .stroke(PipTheme.amberDim.opacity(0.7), lineWidth: 1)
                }
                .padding(10)

            VStack(spacing: 22) {
                Spacer()
                Image(systemName: "waveform.path.ecg.rectangle")
                    .font(.system(size: 42, weight: .light))
                    .foregroundStyle(PipTheme.amber)
                    .shadow(color: PipTheme.amber.opacity(0.45), radius: 12)

                Text("ATTA-BOY")
                    .font(.system(size: 30, weight: .black, design: .monospaced))
                    .tracking(4)
                    .foregroundStyle(PipTheme.amber)

                Rectangle()
                    .fill(PipTheme.amberDim)
                    .frame(height: 1)
                    .padding(.horizontal, 34)

                Text(messages[phase])
                    .font(.system(size: 10, weight: .bold, design: .monospaced))
                    .tracking(1)
                    .multilineTextAlignment(.center)
                    .foregroundStyle(PipTheme.pale)
                    .frame(minHeight: 48)
                    .padding(.horizontal, 24)
                    .contentTransition(.opacity)

                HStack(spacing: 5) {
                    ForEach(0..<messages.count, id: \.self) { index in
                        Capsule()
                            .fill(index <= phase ? PipTheme.amber : PipTheme.amberDim.opacity(0.25))
                            .frame(height: 3)
                    }
                }
                .padding(.horizontal, 36)

                Spacer()

                Text("UNOFFICIAL FALLOUT: LONDON COMPANION")
                    .font(.system(size: 7, weight: .medium, design: .monospaced))
                    .tracking(1)
                    .foregroundStyle(PipTheme.muted)
                    .padding(.bottom, 26)
            }
            .padding(.vertical, 24)

            GeometryReader { proxy in
                Path { path in
                    stride(from: 0, to: proxy.size.height, by: 4).forEach { y in
                        path.move(to: CGPoint(x: 0, y: y))
                        path.addLine(to: CGPoint(x: proxy.size.width, y: y))
                    }
                }
                .stroke(PipTheme.amber.opacity(0.035), lineWidth: 0.7)
            }
            .padding(10)
            .allowsHitTesting(false)
        }
        .task {
            for index in messages.indices {
                withAnimation(.easeInOut(duration: 0.2)) { phase = index }
                try? await Task.sleep(for: .milliseconds(index == messages.count - 1 ? 1200 : 520))
            }
            onComplete()
        }
    }
}
