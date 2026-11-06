import SwiftUI

struct LimbConditionPanel: View {
    let conditions: [String: Int]

    private let regions = [
        ("HEAD", "HEAD"), ("TORSO", "TORSO"),
        ("LEFT ARM", "LEFT ARM"), ("RIGHT ARM", "RIGHT ARM"),
        ("LEFT LEG", "LEFT LEG"), ("RIGHT LEG", "RIGHT LEG")
    ]

    private func value(_ key: String) -> Int? {
        conditions[key] ?? conditions[key.replacingOccurrences(of: "LEFT ", with: "L ").replacingOccurrences(of: "RIGHT ", with: "R ")]
    }

    private func state(_ value: Int) -> String {
        if value <= 0 { return "CRIPPLED" }
        if value < 25 { return "CRITICAL" }
        if value < 50 { return "DAMAGED" }
        if value < 100 { return "WOUNDED" }
        return "HEALTHY"
    }

    private func color(_ value: Int) -> Color {
        if value <= 0 || value < 25 { return PipTheme.danger }
        if value < 50 { return PipTheme.amber }
        return PipTheme.pale
    }

    private func illustrationName(_ key: String, value: Int) -> String {
        let part: String
        switch key {
        case "HEAD": part = "head"
        case "TORSO": part = "torso"
        case "LEFT ARM": part = "arm_left"
        case "RIGHT ARM": part = "arm_right"
        case "LEFT LEG": part = "leg_left"
        default: part = "leg_right"
        }
        return "pack_body_\(part)_\(state(value).lowercased())"
    }

    var body: some View {
        PipPanel(title: "BODY // LIMB CONDITION") {
            Text("LIVE BODY-PART CONDITION · VALUES ARE READ FROM THE GAME DATABASE")
                .font(.system(size: 7, design: .monospaced)).foregroundStyle(PipTheme.muted)
            HStack(alignment: .top, spacing: 10) {
                VStack(spacing: 7) {
                    region("LEFT ARM")
                    region("LEFT LEG")
                }.frame(maxWidth: .infinity)
                VStack(spacing: 7) {
                    region("HEAD")
                    region("TORSO")
                }.frame(maxWidth: .infinity)
                VStack(spacing: 7) {
                    region("RIGHT ARM")
                    region("RIGHT LEG")
                }.frame(maxWidth: .infinity)
            }
            ForEach(regions, id: \.0) { region in
                if let current = value(region.1) {
                    HStack {
                        Text(region.0).foregroundStyle(PipTheme.muted)
                        Spacer()
                        Text("\(current)%  //  \(state(current))")
                            .foregroundStyle(color(current))
                    }
                    .font(.system(size: 8, weight: .bold, design: .monospaced))
                }
            }
            if regions.allSatisfy({ value($0.1) == nil }) {
                Text("WAITING FOR LIMB CONDITION DATA")
                    .font(.system(size: 8, design: .monospaced)).foregroundStyle(PipTheme.muted)
            }
        }
    }

    @ViewBuilder
    private func region(_ key: String) -> some View {
        if let current = value(key) {
            VStack(spacing: 3) {
                Text(key.replacingOccurrences(of: "LEFT ", with: "L ").replacingOccurrences(of: "RIGHT ", with: "R "))
                    .font(.system(size: 7, weight: .bold, design: .monospaced))
                    .foregroundStyle(PipTheme.pale)
                Image(illustrationName(key, value: current))
                    .resizable()
                    .scaledToFit()
                    .frame(height: 42)
                    .accessibilityLabel("\(key) \(state(current).lowercased())")
                Text("\(current)%")
                    .font(.system(size: 12, weight: .black, design: .monospaced))
                    .foregroundStyle(color(current))
                GeometryReader { proxy in
                    ZStack(alignment: .leading) {
                        Rectangle().fill(PipTheme.amberDim.opacity(0.2))
                        Rectangle().fill(color(current)).frame(width: proxy.size.width * CGFloat(min(100, max(0, current))) / 100)
                    }
                }.frame(height: 4)
                Text(state(current))
                    .font(.system(size: 6, weight: .bold, design: .monospaced))
                    .foregroundStyle(color(current))
            }
            .padding(5)
            .frame(maxWidth: .infinity)
            .overlay(Rectangle().stroke(PipTheme.amberDim.opacity(0.55)))
        } else {
            VStack {
                Text(key).font(.system(size: 7, design: .monospaced))
                Text("--").font(.system(size: 12, design: .monospaced))
                Text("NO DATA").font(.system(size: 6, design: .monospaced))
            }
            .foregroundStyle(PipTheme.muted)
            .padding(5)
            .frame(maxWidth: .infinity)
            .overlay(Rectangle().stroke(PipTheme.amberDim.opacity(0.25)))
        }
    }
}