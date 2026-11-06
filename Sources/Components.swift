import SwiftUI

struct ScreenHeader: View {
    @EnvironmentObject private var state: AttaBoyState
    let title: String
    var subtitle: String = "PERSONAL INFORMATION PROCESSOR"
    var body: some View {
        VStack(alignment: .leading, spacing: 5) {
            HStack(alignment: .firstTextBaseline) {
                Text(title).font(.system(size: 25, weight: .black, design: .monospaced)).tracking(2)
                Spacer()
                Text(state.gameWorld == .london ? "LONDON // 202" : "COMMONWEALTH // 2287").font(.system(size: 9, weight: .bold, design: .monospaced)).foregroundStyle(PipTheme.amberDim)
            }
            Text(subtitle).font(.system(size: 9, weight: .medium, design: .monospaced)).tracking(1.6).foregroundStyle(PipTheme.muted)
            Rectangle().fill(PipTheme.amberDim).frame(height: 1).padding(.top, 7)
        }
        .foregroundStyle(PipTheme.amber)
        .padding(.bottom, 8)
    }
}

struct PipPanel<Content: View>: View {
    let title: String
    @ViewBuilder var content: Content
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text(title).font(.system(size: 11, weight: .bold, design: .monospaced)).tracking(1.5)
                Spacer()
                Image(systemName: "chevron.down").font(.system(size: 9, weight: .bold))
            }
            .foregroundStyle(PipTheme.amberDim)
            content
        }
        .padding(14)
        .background(PipTheme.panel, in: RoundedRectangle(cornerRadius: 7))
        .overlay(RoundedRectangle(cornerRadius: 7).stroke(PipTheme.amberDim.opacity(0.45), lineWidth: 1))
    }
}

struct MeterRow: View {
    let title: String
    let value: Int
    var color: Color = PipTheme.amber
    var body: some View {
        VStack(alignment: .leading, spacing: 5) {
            HStack {
                Text(title).font(.system(size: 10, weight: .bold, design: .monospaced))
                Spacer()
                Text("\(value)%").font(.system(size: 10, weight: .bold, design: .monospaced)).monospacedDigit()
            }
            GeometryReader { proxy in
                ZStack(alignment: .leading) {
                    Capsule().fill(PipTheme.background)
                    Capsule().fill(color).frame(width: proxy.size.width * CGFloat(min(max(value, 0), 100)) / 100)
                }
            }
            .frame(height: 7)
        }
        .foregroundStyle(PipTheme.pale)
    }
}

struct ValueTile: View {
    let label: String
    let value: String
    let symbol: String
    var body: some View {
        VStack(alignment: .leading, spacing: 7) {
            Image(systemName: symbol).font(.system(size: 15)).foregroundStyle(PipTheme.amberDim)
            Text(value).font(.system(size: 20, weight: .bold, design: .monospaced)).foregroundStyle(PipTheme.pale).minimumScaleFactor(0.7).lineLimit(1)
            Text(label).font(.system(size: 9, weight: .bold, design: .monospaced)).tracking(1).foregroundStyle(PipTheme.muted)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(12)
        .background(PipTheme.panelRaised, in: RoundedRectangle(cornerRadius: 6))
    }
}

struct TerminalButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .foregroundStyle(PipTheme.background)
            .background(configuration.isPressed ? PipTheme.pale : PipTheme.amber, in: RoundedRectangle(cornerRadius: 5))
            .scaleEffect(configuration.isPressed ? 0.97 : 1)
    }
}
