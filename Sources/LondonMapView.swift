import SwiftUI
import UIKit

struct LondonMapView: View {
    @EnvironmentObject private var state: AttaBoyState

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 15) {
                    ScreenHeader(title: "LONDON MAP", subtitle: "GAME WORLD POSITION & LOCAL MAP")
                    PipPanel(title: "PLAYER POSITION") {
                        if let position = state.playerPosition {
                            HStack {
                                coordinate("X", value: position.x)
                                coordinate("Y", value: position.y)
                                coordinate("ROT", value: position.rotation)
                            }
                        } else {
                            Text(state.isLiveData ? "PLAYER POSITION NOT PRESENT IN CURRENT DATABASE" : "CONNECT TO FALLOUT TO READ PLAYER POSITION")
                                .font(.system(size: 9, design: .monospaced)).foregroundStyle(PipTheme.muted)
                        }
                        Button("REQUEST LOCAL MAP SNAPSHOT") { state.requestLocalMapSnapshot() }
                            .font(.system(size: 9, weight: .black, design: .monospaced))
                            .buttonStyle(.borderedProminent).tint(PipTheme.amber)
                    }
                    PipPanel(title: "LOCAL MAP SNAPSHOT") {
                        if let map = state.localMap, let image = makeImage(map) {
                            VStack(spacing: 8) {
                                Image(uiImage: image)
                                    .resizable().interpolation(.none).scaledToFit()
                                    .frame(maxWidth: .infinity)
                                    .background(Color.black)
                                Text("\(map.width) × \(map.height) · \(map.pixels.count) BYTES")
                                    .font(.system(size: 8, design: .monospaced)).foregroundStyle(PipTheme.muted)
                            }
                        } else {
                            Text("NO LOCAL MAP SNAPSHOT RECEIVED. REQUEST ONE WHILE CONNECTED IN-GAME.")
                                .font(.system(size: 9, design: .monospaced)).foregroundStyle(PipTheme.muted)
                        }
                    }
                    PipPanel(title: "LONDON DISTRICT INDEX") {
                        Text("SCHEMATIC REFERENCE ONLY · NOT THE GAME'S WORLD MAP")
                            .font(.system(size: 8, design: .monospaced)).foregroundStyle(PipTheme.muted)
                        GeometryReader { proxy in
                            let size = proxy.size
                            ZStack {
                                Canvas { context, canvasSize in
                                    var grid = Path()
                                    stride(from: 0.0, through: canvasSize.width, by: 22).forEach { x in
                                        grid.move(to: CGPoint(x: x, y: 0))
                                        grid.addLine(to: CGPoint(x: x, y: canvasSize.height))
                                    }
                                    stride(from: 0.0, through: canvasSize.height, by: 22).forEach { y in
                                        grid.move(to: CGPoint(x: 0, y: y))
                                        grid.addLine(to: CGPoint(x: canvasSize.width, y: y))
                                    }
                                    context.stroke(grid, with: .color(PipTheme.amber.opacity(0.10)), lineWidth: 0.5)
                                    var river = Path()
                                    river.move(to: CGPoint(x: 0, y: canvasSize.height * 0.69))
                                    river.addCurve(to: CGPoint(x: canvasSize.width, y: canvasSize.height * 0.54), control1: CGPoint(x: canvasSize.width * 0.35, y: canvasSize.height * 0.53), control2: CGPoint(x: canvasSize.width * 0.60, y: canvasSize.height * 0.88))
                                    context.stroke(river, with: .color(PipTheme.amberDim.opacity(0.9)), style: StrokeStyle(lineWidth: 8, lineCap: .round))
                                    context.stroke(river, with: .color(PipTheme.background), style: StrokeStyle(lineWidth: 5, lineCap: .round))
                                }
                                ForEach(District.all) { district in
                                    Button { state.selectDistrict(district) } label: {
                                        VStack(spacing: 4) {
                                            Image(systemName: state.selectedDistrictID == district.id ? "mappin.and.ellipse" : "circle.fill")
                                                .font(.system(size: state.selectedDistrictID == district.id ? 23 : 13, weight: .bold))
                                            Text(district.name).font(.system(size: 8, weight: .black, design: .monospaced)).fixedSize()
                                        }
                                        .foregroundStyle(state.selectedDistrictID == district.id ? PipTheme.pale : PipTheme.amber)
                                        .padding(6)
                                        .background(state.selectedDistrictID == district.id ? PipTheme.panelRaised : PipTheme.background.opacity(0.65), in: RoundedRectangle(cornerRadius: 5))
                                    }
                                    .buttonStyle(.plain)
                                    .position(x: size.width * district.x, y: size.height * district.y)
                                }
                            }
                        }
                        .frame(height: 300).clipped()
                    }
                    if let status = state.lastActionStatus {
                        Text(status).font(.system(size: 8, design: .monospaced)).foregroundStyle(PipTheme.amber)
                    }
                }.padding(16)
            }
            .background(PipTheme.background)
            .toolbar(.hidden, for: .navigationBar)
        }
    }

    private func coordinate(_ title: String, value: Double) -> some View {
        VStack(alignment: .leading, spacing: 3) {
            Text(title).font(.system(size: 8, weight: .bold, design: .monospaced)).foregroundStyle(PipTheme.muted)
            Text(String(format: "%.2f", value)).font(.system(size: 12, weight: .bold, design: .monospaced)).foregroundStyle(PipTheme.pale)
        }.frame(maxWidth: .infinity, alignment: .leading)
    }

    private func makeImage(_ map: PipboyLocalMapUpdate) -> UIImage? {
        guard map.width > 0, map.height > 0,
              map.width <= 4096, map.height <= 4096,
              map.pixels.count == map.width * map.height,
              let provider = CGDataProvider(data: map.pixels as CFData),
              let cgImage = CGImage(
                width: map.width, height: map.height,
                bitsPerComponent: 8, bitsPerPixel: 8,
                bytesPerRow: map.width,
                space: CGColorSpaceCreateDeviceGray(),
                bitmapInfo: CGBitmapInfo(rawValue: 0),
                provider: provider, decode: nil,
                shouldInterpolate: false, intent: .defaultIntent
              ) else { return nil }
        return UIImage(cgImage: cgImage)
    }
}
