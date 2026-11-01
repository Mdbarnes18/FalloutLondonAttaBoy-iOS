import SwiftUI

struct LondonMapView: View {
    @EnvironmentObject private var state: AttaBoyState
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 15) {
                    ScreenHeader(title: "LONDON MAP", subtitle: "REGIONAL CARTOGRAPHIC DATA")
                    PipPanel(title: "CITY GRID // SCHEMATIC") {
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
                                    Button {
                                        state.selectDistrict(district)
                                    } label: {
                                        VStack(spacing: 4) {
                                            Image(systemName: state.selectedDistrictID == district.id ? "mappin.and.ellipse" : "circle.fill")
                                                .font(.system(size: state.selectedDistrictID == district.id ? 23 : 13, weight: .bold))
                                            Text(district.name)
                                                .font(.system(size: 8, weight: .black, design: .monospaced))
                                                .fixedSize()
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
                        .frame(height: 350)
                        .clipped()
                    }
                    PipPanel(title: "SELECTED LOCATION") {
                        HStack {
                            Image(systemName: "mappin.circle.fill").font(.system(size: 27)).foregroundStyle(PipTheme.amber)
                            VStack(alignment: .leading, spacing: 4) {
                                Text(state.selectedDistrict.name).font(.system(size: 14, weight: .black, design: .monospaced)).foregroundStyle(PipTheme.pale)
                                Text(state.selectedDistrict.subtitle.uppercased()).font(.system(size: 9, design: .monospaced)).foregroundStyle(PipTheme.muted)
                            }
                            Spacer()
                            Text("UNKNOWN").font(.system(size: 8, weight: .bold, design: .monospaced)).foregroundStyle(PipTheme.amberDim)
                        }
                    }
                    Text("MAP DATA IS A NON-NAVIGATIONAL FAN-MADE SCHEMATIC")
                        .font(.system(size: 8, weight: .medium, design: .monospaced)).foregroundStyle(PipTheme.muted)
                }
                .padding(16)
            }
            .background(PipTheme.background)
            .toolbar(.hidden, for: .navigationBar)
        }
    }
}
