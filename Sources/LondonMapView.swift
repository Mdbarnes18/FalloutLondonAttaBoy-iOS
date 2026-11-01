import SwiftUI
import UIKit

struct LondonMapView: View {
    @EnvironmentObject private var state: AttaBoyState
    @State private var showingTravelConfirm = false
    @State private var selectedTravelLocation: LiveMapLocation?

    private var plottedLocations: [LiveMapLocation] {
        state.liveMapLocations.filter { $0.visible || $0.discovered }
    }

    private var worldBounds: (minX: Double, maxX: Double, minY: Double, maxY: Double)? {
        var coordinates = plottedLocations.map { ($0.x, $0.y) }
        if let player = state.playerPosition {
            coordinates.append((player.x, player.y))
        }
        guard !coordinates.isEmpty else { return nil }

        let minX = coordinates.map(\.0).min() ?? 0
        let maxX = coordinates.map(\.0).max() ?? 0
        let minY = coordinates.map(\.1).min() ?? 0
        let maxY = coordinates.map(\.1).max() ?? 0
        let spanX = max(maxX - minX, 100)
        let spanY = max(maxY - minY, 100)
        return (
            minX: minX - spanX * 0.08,
            maxX: maxX + spanX * 0.08,
            minY: minY - spanY * 0.08,
            maxY: maxY + spanY * 0.08
        )
    }

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 15) {
                    ScreenHeader(title: "LONDON MAP", subtitle: "LIVE GAME WORLD & LOCAL MAP")
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
                        HStack(spacing: 7) {
                            Button("REQUEST LOCAL MAP") { state.requestLocalMapSnapshot() }
                                .font(.system(size: 8, weight: .black, design: .monospaced))
                                .buttonStyle(.borderedProminent).tint(PipTheme.amber)
                            Button("MARK PLAYER") {
                                if let position = state.playerPosition {
                                    state.setCustomMapMarker(x: position.x, y: position.y)
                                }
                            }
                            .font(.system(size: 8, weight: .bold, design: .monospaced))
                            .buttonStyle(.bordered).tint(PipTheme.amber)
                            .disabled(!state.hasPlayerPosition)
                            Button("CLEAR MARKER") { state.clearCustomMapMarker() }
                                .font(.system(size: 8, weight: .bold, design: .monospaced))
                                .buttonStyle(.bordered).tint(PipTheme.amber)
                        }
                    }

                    PipPanel(title: "LOCAL MAP SNAPSHOT") {
                        if let map = state.localMap, let image = makeImage(map) {
                            VStack(spacing: 8) {
                                GeometryReader { proxy in
                                    ZStack(alignment: .topLeading) {
                                        Image(uiImage: image)
                                            .resizable()
                                            .interpolation(.none)
                                            .frame(width: proxy.size.width, height: proxy.size.height)
                                        if let player = state.playerPosition,
                                           let point = localMapPoint(playerX: player.x, playerY: player.y, map: map) {
                                            ZStack {
                                                Circle().fill(PipTheme.background.opacity(0.85)).frame(width: 24, height: 24)
                                                Image(systemName: "location.north.fill")
                                                    .font(.system(size: 13, weight: .black))
                                                    .foregroundStyle(PipTheme.amber)
                                            }
                                            .position(x: point.x * proxy.size.width, y: point.y * proxy.size.height)
                                            .shadow(color: .black, radius: 3)
                                        }
                                    }
                                }
                                .aspectRatio(CGFloat(map.width) / CGFloat(map.height), contentMode: .fit)
                                Text("\(map.width) × \(map.height) · \(map.pixels.count) PIXELS")
                                    .font(.system(size: 8, design: .monospaced)).foregroundStyle(PipTheme.muted)
                            }
                        } else {
                            Text("NO LOCAL MAP SNAPSHOT RECEIVED. REQUEST ONE WHILE CONNECTED IN-GAME.")
                                .font(.system(size: 9, design: .monospaced)).foregroundStyle(PipTheme.muted)
                        }
                    }

                    PipPanel(title: "LIVE WORLD PLOT // \(plottedLocations.count) LOCATIONS") {
                        Text("POSITIONS AND MARKERS COME FROM THE CONNECTED GAME DATABASE. THIS IS A COORDINATE PLOT, NOT A GEOGRAPHICALLY VERIFIED LONDON BASEMAP.")
                            .font(.system(size: 8, design: .monospaced)).foregroundStyle(PipTheme.muted)
                            .fixedSize(horizontal: false, vertical: true)
                        if let bounds = worldBounds {
                            GeometryReader { proxy in
                                ZStack {
                                    Canvas { context, size in
                                        var grid = Path()
                                        for step in 0...8 {
                                            let x = size.width * CGFloat(step) / 8
                                            let y = size.height * CGFloat(step) / 8
                                            grid.move(to: CGPoint(x: x, y: 0))
                                            grid.addLine(to: CGPoint(x: x, y: size.height))
                                            grid.move(to: CGPoint(x: 0, y: y))
                                            grid.addLine(to: CGPoint(x: size.width, y: y))
                                        }
                                        context.stroke(grid, with: .color(PipTheme.amber.opacity(0.12)), lineWidth: 0.6)
                                        context.stroke(
                                            Path(roundedRect: CGRect(origin: .zero, size: size), cornerRadius: 3),
                                            with: .color(PipTheme.amberDim.opacity(0.65)),
                                            lineWidth: 1
                                        )
                                    }

                                    ForEach(plottedLocations) { location in
                                        let point = plotPoint(x: location.x, y: location.y, bounds: bounds, size: proxy.size)
                                        Button {
                                            selectedTravelLocation = location
                                            showingTravelConfirm = true
                                        } label: {
                                            VStack(spacing: 2) {
                                                Image(systemName: location.cleared ? "checkmark.circle.fill" : "mappin.circle.fill")
                                                    .font(.system(size: 17, weight: .bold))
                                                Text(location.name.uppercased())
                                                    .font(.system(size: 7, weight: .black, design: .monospaced))
                                                    .lineLimit(1)
                                                    .fixedSize()
                                            }
                                            .foregroundStyle(location.discovered ? PipTheme.pale : PipTheme.amber)
                                            .padding(3)
                                            .background(PipTheme.background.opacity(0.88), in: RoundedRectangle(cornerRadius: 3))
                                        }
                                        .buttonStyle(.plain)
                                        .position(point)
                                    }

                                    if let player = state.playerPosition {
                                        let point = plotPoint(x: player.x, y: player.y, bounds: bounds, size: proxy.size)
                                        VStack(spacing: 2) {
                                            Image(systemName: "location.north.circle.fill")
                                                .font(.system(size: 22, weight: .black))
                                            Text("YOU")
                                                .font(.system(size: 7, weight: .black, design: .monospaced))
                                        }
                                        .foregroundStyle(PipTheme.amber)
                                        .shadow(color: .black, radius: 3)
                                        .position(point)
                                        .allowsHitTesting(false)
                                    }
                                }
                            }
                            .frame(height: 310)
                            Text("X \(Int(bounds.minX)) … \(Int(bounds.maxX))     Y \(Int(bounds.minY)) … \(Int(bounds.maxY))")
                                .font(.system(size: 8, design: .monospaced)).foregroundStyle(PipTheme.muted)
                        } else {
                            Text(state.isLiveData ? "THE GAME HAS NOT PROVIDED WORLD LOCATION COORDINATES YET." : "CONNECT TO FALLOUT TO POPULATE THE WORLD PLOT.")
                                .font(.system(size: 9, design: .monospaced)).foregroundStyle(PipTheme.muted)
                                .frame(maxWidth: .infinity, minHeight: 150)
                        }
                    }

                    if !state.liveMapLocations.isEmpty {
                        PipPanel(title: "GAME LOCATION REGISTER // \(state.liveMapLocations.count)") {
                            ForEach(state.liveMapLocations) { location in
                                HStack(spacing: 8) {
                                    VStack(alignment: .leading, spacing: 3) {
                                        Text(location.name.uppercased())
                                            .font(.system(size: 9, weight: .bold, design: .monospaced))
                                            .foregroundStyle(PipTheme.pale)
                                        Text("\(location.visible ? "VISIBLE" : location.discovered ? "DISCOVERED" : "UNDISCOVERED") · \(location.cleared ? "CLEARED" : "NOT CLEARED") · X \(Int(location.x)) Y \(Int(location.y))")
                                            .font(.system(size: 7, design: .monospaced)).foregroundStyle(PipTheme.muted)
                                    }
                                    Spacer()
                                    Button("TRAVEL") {
                                        selectedTravelLocation = location
                                        showingTravelConfirm = true
                                    }
                                    .font(.system(size: 8, weight: .black, design: .monospaced))
                                    .buttonStyle(.bordered).tint(PipTheme.amber)
                                    .disabled(!location.discovered && !location.visible)
                                }.padding(.vertical, 5)
                            }
                        }
                    }

                    if let status = state.lastActionStatus {
                        Text(status).font(.system(size: 8, design: .monospaced)).foregroundStyle(PipTheme.amber)
                    }
                }.padding(16)
            }
            .background(PipTheme.background)
            .toolbar(.hidden, for: .navigationBar)
            .confirmationDialog(
                "Fast travel to \(selectedTravelLocation?.name ?? "this location")?",
                isPresented: $showingTravelConfirm,
                titleVisibility: .visible
            ) {
                Button("FAST TRAVEL", role: .destructive) {
                    if let selectedTravelLocation { state.fastTravel(to: selectedTravelLocation) }
                }
                Button("CANCEL", role: .cancel) { selectedTravelLocation = nil }
            } message: {
                Text("The game will move your character. The request is subject to the game's fast-travel rules.")
            }
        }
    }

    private func coordinate(_ title: String, value: Double) -> some View {
        VStack(alignment: .leading, spacing: 3) {
            Text(title).font(.system(size: 8, weight: .bold, design: .monospaced)).foregroundStyle(PipTheme.muted)
            Text(String(format: "%.2f", value)).font(.system(size: 12, weight: .bold, design: .monospaced)).foregroundStyle(PipTheme.pale)
        }.frame(maxWidth: .infinity, alignment: .leading)
    }

    private func plotPoint(
        x: Double,
        y: Double,
        bounds: (minX: Double, maxX: Double, minY: Double, maxY: Double),
        size: CGSize
    ) -> CGPoint {
        let width = max(bounds.maxX - bounds.minX, 1)
        let height = max(bounds.maxY - bounds.minY, 1)
        let px = (x - bounds.minX) / width
        let py = 1 - (y - bounds.minY) / height
        return CGPoint(
            x: CGFloat(min(max(px, 0), 1)) * size.width,
            y: CGFloat(min(max(py, 0), 1)) * size.height
        )
    }

    private func localMapPoint(playerX: Double, playerY: Double, map: PipboyLocalMapUpdate) -> CGPoint? {
        let nw = SIMD2<Double>(Double(map.northWest.x), Double(map.northWest.y))
        let east = SIMD2<Double>(Double(map.northEast.x) - nw.x, Double(map.northEast.y) - nw.y)
        let south = SIMD2<Double>(Double(map.southWest.x) - nw.x, Double(map.southWest.y) - nw.y)
        let delta = SIMD2<Double>(playerX - nw.x, playerY - nw.y)
        let determinant = east.x * south.y - east.y * south.x
        guard abs(determinant) > 0.000001 else { return nil }
        let u = (delta.x * south.y - delta.y * south.x) / determinant
        let v = (east.x * delta.y - east.y * delta.x) / determinant
        guard u.isFinite, v.isFinite, (0...1).contains(u), (0...1).contains(v) else { return nil }
        return CGPoint(x: CGFloat(u), y: CGFloat(v))
    }

    private func makeImage(_ map: PipboyLocalMapUpdate) -> UIImage? {
        guard map.width > 0, map.height > 0,
              map.width <= 4096, map.height <= 4096,
              map.pixels.count == map.width * map.height,
              let provider = CGDataProvider(data: map.pixels as CFData) else { return nil }
        var palette = [UInt8]()
        palette.reserveCapacity(256 * 3)
        for index in 0..<256 {
            palette.append(UInt8(index / 4))
            palette.append(UInt8(index))
            palette.append(UInt8(index / 2))
        }
        guard let colorSpace = palette.withUnsafeBufferPointer({ buffer in
            CGColorSpace(
                indexedBaseSpace: CGColorSpaceCreateDeviceRGB(),
                last: 255,
                colorTable: buffer.baseAddress!
            )
        }) else { return nil }
        guard let cgImage = CGImage(
            width: map.width, height: map.height,
            bitsPerComponent: 8, bitsPerPixel: 8,
            bytesPerRow: map.width,
            space: colorSpace,
            bitmapInfo: CGBitmapInfo(rawValue: 0),
            provider: provider, decode: nil,
            shouldInterpolate: false, intent: .defaultIntent
        ) else { return nil }
        return UIImage(cgImage: cgImage)
    }
}
