import SwiftUI
import UniformTypeIdentifiers

private struct DiagnosticTextDocument: FileDocument {
    static var readableContentTypes: [UTType] { [.plainText] }
    var text: String

    init(text: String) { self.text = text }

    init(configuration: ReadConfiguration) throws {
        text = String(decoding: configuration.file.regularFileContents ?? Data(), as: UTF8.self)
    }

    func fileWrapper(configuration: WriteConfiguration) throws -> FileWrapper {
        FileWrapper(regularFileWithContents: Data(text.utf8))
    }
}

struct DataBrowserView: View {
    @EnvironmentObject private var state: AttaBoyState
    @State private var search = ""
    @State private var showingExporter = false
    @State private var showingLogExporter = false
    @State private var exportError: String?
    @State private var logExportError: String?

    private var filteredEntries: [LiveDatabaseEntry] {
        guard !search.isEmpty else { return state.databaseEntries.sorted { $0.path.localizedCaseInsensitiveCompare($1.path) == .orderedAscending } }
        return state.databaseEntries.filter {
            $0.path.localizedCaseInsensitiveContains(search) || $0.value.localizedCaseInsensitiveContains(search)
        }.sorted { $0.path.localizedCaseInsensitiveCompare($1.path) == .orderedAscending }
    }

    private var diagnosticText: String { state.diagnosticExportText }

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 12) {
                    ScreenHeader(title: "DATA BROWSER", subtitle: "LIVE PIP-BOY DATABASE INSPECTOR")
                    PipPanel(title: "DIAGNOSTIC EXPORT") {
                        Text("Export the complete decoded database tree as a plain-text file for GitHub issues and troubleshooting.")
                            .font(.system(size: 9, design: .monospaced)).foregroundStyle(PipTheme.muted)
                        HStack {
                            Text("\(state.databaseEntries.count) VALUES")
                                .font(.system(size: 9, weight: .bold, design: .monospaced)).foregroundStyle(PipTheme.pale)
                            Spacer()
                            Button("SAVE TXT") { showingExporter = true }
                                .font(.system(size: 9, weight: .black, design: .monospaced))
                                .buttonStyle(.borderedProminent).tint(PipTheme.amber)
                                .disabled(state.databaseEntries.isEmpty)
                        }
                        if let exportError {
                            Text(exportError).font(.system(size: 8, design: .monospaced)).foregroundStyle(PipTheme.danger)
                        }
                        Text("The export includes decoded game data and may contain personal save details. Review before sharing.")
                            .font(.system(size: 8, design: .monospaced)).foregroundStyle(PipTheme.muted)
                    }
                    PipPanel(title: "DATA UPDATE LOGGER") {
                        Toggle("CAPTURE LIVE UPDATES", isOn: Binding(
                            get: { state.dataUpdateLoggerEnabled },
                            set: { state.setDataUpdateLoggerEnabled($0) }
                        ))
                        .font(.system(size: 9, weight: .bold, design: .monospaced))
                        .tint(PipTheme.amber)
                        HStack {
                            Text("\(state.dataUpdateLog.count) / 10,000 EVENTS")
                                .font(.system(size: 8, weight: .bold, design: .monospaced))
                                .foregroundStyle(PipTheme.muted)
                            Spacer()
                            Button("CLEAR") { state.clearDataUpdateLog() }
                                .font(.system(size: 8, weight: .black, design: .monospaced))
                            Button("SAVE LOG") { showingLogExporter = true }
                                .font(.system(size: 8, weight: .black, design: .monospaced))
                                .disabled(state.dataUpdateLog.isEmpty)
                        }
                        if let logExportError {
                            Text(logExportError).font(.system(size: 8, design: .monospaced)).foregroundStyle(PipTheme.danger)
                        }
                        if state.dataUpdateLog.isEmpty {
                            Text("ENABLE LOGGING TO CAPTURE LIVE RECORD UPDATES")
                                .font(.system(size: 8, design: .monospaced)).foregroundStyle(PipTheme.muted)
                        } else {
                            ForEach(state.dataUpdateLog.suffix(250).reversed(), id: \.self) { entry in
                                Text(entry)
                                    .font(.system(size: 7, design: .monospaced))
                                    .foregroundStyle(PipTheme.pale)
                                    .textSelection(.enabled)
                                    .frame(maxWidth: .infinity, alignment: .leading)
                            }
                        }
                    }
                    TextField("SEARCH PATH OR VALUE", text: $search)
                        .font(.system(size: 10, design: .monospaced)).padding(9)
                        .background(PipTheme.panel)
                        .overlay(Rectangle().stroke(PipTheme.amberDim.opacity(0.5)))
                        .foregroundStyle(PipTheme.pale)
                    PipPanel(title: "DATABASE NODES // \(filteredEntries.count)") {
                        if filteredEntries.isEmpty {
                            Text(state.databaseEntries.isEmpty ? "WAITING FOR GAME DATA" : "NO MATCHING VALUES")
                                .font(.system(size: 9, design: .monospaced)).foregroundStyle(PipTheme.muted)
                        }
                        ForEach(filteredEntries) { entry in
                            VStack(alignment: .leading, spacing: 3) {
                                Text(entry.path)
                                    .font(.system(size: 8, weight: .bold, design: .monospaced))
                                    .foregroundStyle(PipTheme.amber)
                                    .textSelection(.enabled)
                                Text(entry.value)
                                    .font(.system(size: 9, design: .monospaced))
                                    .foregroundStyle(PipTheme.pale)
                                    .textSelection(.enabled)
                            }
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .padding(.vertical, 5)
                            Rectangle().fill(PipTheme.amberDim.opacity(0.18)).frame(height: 1)
                        }
                    }
                }
                .padding(12)
            }
            .background(PipTheme.background)
            .fileExporter(
                isPresented: $showingExporter,
                document: DiagnosticTextDocument(text: diagnosticText),
                contentType: .plainText,
                defaultFilename: "Atta-Boy-Diagnostics-\(Date.now.formatted(.iso8601.year().month().day())).txt"
            ) { result in
                if case .failure(let error) = result { exportError = error.localizedDescription }
                else { exportError = nil }
            }
            .fileExporter(
                isPresented: $showingLogExporter,
                document: DiagnosticTextDocument(text: state.dataUpdateLog.joined(separator: "\n")),
                contentType: .plainText,
                defaultFilename: "Atta-Boy-Update-Log-\(Date.now.formatted(.iso8601.year().month().day())).txt"
            ) { result in
                if case .failure(let error) = result { logExportError = error.localizedDescription }
                else { logExportError = nil }
            }
        }
        .tint(PipTheme.amber)
    }
}
