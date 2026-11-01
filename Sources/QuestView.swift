import SwiftUI
import UniformTypeIdentifiers
import UIKit

private struct DatabaseBrowserItem: Identifiable {
    let path: String
    let label: String
    let value: String?
    let isFolder: Bool
    var id: String { path }
}

private struct DatabaseTextDocument: FileDocument {
    static var readableContentTypes: [UTType] { [.plainText] }
    let text: String
    init(text: String) { self.text = text }
    init(configuration: ReadConfiguration) throws {
        text = String(data: configuration.file.regularFileContents ?? Data(), encoding: .utf8) ?? ""
    }
    func fileWrapper(configuration: WriteConfiguration) throws -> FileWrapper {
        FileWrapper(regularFileWithContents: Data(text.utf8))
    }
}

struct QuestView: View {
    @EnvironmentObject private var state: AttaBoyState
    @State private var expandedQuestID: String?
    @State private var databaseSearch = ""
    @State private var databaseBrowserPath = ""
    @State private var showingDatabaseExporter = false
    @State private var databaseCopied = false

    private var filteredDatabaseEntries: [LiveDatabaseEntry] {
        guard !databaseSearch.isEmpty else { return state.databaseEntries }
        return state.databaseEntries.filter {
            $0.path.localizedCaseInsensitiveContains(databaseSearch) ||
            $0.value.localizedCaseInsensitiveContains(databaseSearch)
        }
    }

    private var databaseExportText: String {
        var output = "FALLOUT: LONDON ATTA-BOY DATA EXPORT\\n"
        output += "Generated from the current live game database\\n"
        output += "Entries: \\(state.databaseEntries.count)\\n\\n"
        for entry in state.databaseEntries { output += "\\(entry.path) = \\(entry.value)\\n" }
        return output
    }

    private var visibleDatabaseItems: [DatabaseBrowserItem] {
        var grouped: [String: DatabaseBrowserItem] = [:]
        let current = databaseBrowserPath
        for entry in state.databaseEntries {
            let relative: String
            if current.isEmpty { relative = entry.path }
            else if entry.path.hasPrefix(current + ".") {
                relative = String(entry.path.dropFirst(current.count + 1))
            } else if entry.path.hasPrefix(current + "[") {
                relative = String(entry.path.dropFirst(current.count))
            } else { continue }
            guard !relative.isEmpty else { continue }

            let segment: String
            if relative.first == "[" {
                guard let close = relative.firstIndex(of: "]") else { continue }
                segment = String(relative[...close])
            } else {
                let end = relative.firstIndex(where: { $0 == "." || $0 == "[" }) ?? relative.endIndex
                segment = String(relative[..<end])
            }
            guard !segment.isEmpty else { continue }
            let suffix = relative.dropFirst(segment.count)
            let hasChildren = !suffix.isEmpty
            let childPath = current.isEmpty
                ? segment
                : (segment.first == "[" ? current + segment : current + "." + segment)
            let previous = grouped[childPath]
            grouped[childPath] = DatabaseBrowserItem(
                path: childPath,
                label: segment,
                value: hasChildren ? previous?.value : entry.value,
                isFolder: hasChildren || (previous?.isFolder ?? false)
            )
        }
        return grouped.values.sorted {
            if $0.isFolder != $1.isFolder { return $0.isFolder }
            return $0.label.localizedStandardCompare($1.label) == .orderedAscending
        }
    }

    private func moveDatabaseBrowserUp() {
        guard !databaseBrowserPath.isEmpty else { return }
        if let dot = databaseBrowserPath.lastIndex(of: ".") {
            databaseBrowserPath = String(databaseBrowserPath[..<dot])
        } else if let bracket = databaseBrowserPath.lastIndex(of: "[") {
            databaseBrowserPath = String(databaseBrowserPath[..<bracket])
        } else {
            databaseBrowserPath = ""
        }
    }

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 15) {
                    ScreenHeader(title: "QUEST DATA", subtitle: "LIVE OBJECTIVES & FIELD RECORDS")
                    if !state.isLiveData {
                        PipPanel(title: "DATA LINK OFFLINE") {
                            Text("Connect to Fallout to load your active quests, miscellaneous objectives and completion states.")
                                .font(.system(size: 10, design: .monospaced)).foregroundStyle(PipTheme.muted)
                        }
                    } else if state.liveQuests.isEmpty {
                        PipPanel(title: "NO QUESTS RECEIVED") {
                            Text("The current game database has not exposed enabled quest entries.")
                                .font(.system(size: 10, design: .monospaced)).foregroundStyle(PipTheme.muted)
                        }
                    } else {
                        let activeCount = state.liveQuests.filter(\.active).count
                        PipPanel(title: "QUEST REGISTER") {
                            HStack {
                                Text("\(state.liveQuests.count) ENABLED QUESTS")
                                    .font(.system(size: 10, weight: .bold, design: .monospaced)).foregroundStyle(PipTheme.pale)
                                Spacer()
                                Text("\(activeCount) ACTIVE").font(.system(size: 9, design: .monospaced)).foregroundStyle(PipTheme.amber)
                            }
                        }
                        ForEach(state.liveQuests) { quest in
                            PipPanel(title: quest.active ? "ACTIVE OBJECTIVE" : "QUEST RECORD") {
                                Button {
                                    expandedQuestID = expandedQuestID == quest.id ? nil : quest.id
                                } label: {
                                    HStack {
                                        VStack(alignment: .leading, spacing: 4) {
                                            Text(quest.title.uppercased())
                                                .font(.system(size: 11, weight: .black, design: .monospaced))
                                                .foregroundStyle(PipTheme.pale)
                                            if !quest.detail.isEmpty {
                                                Text(quest.detail).font(.system(size: 9, design: .monospaced))
                                                    .foregroundStyle(PipTheme.muted).multilineTextAlignment(.leading)
                                            }
                                        }
                                        Spacer()
                                        Text(quest.active ? "ACTIVE" : "VIEW")
                                            .font(.system(size: 8, weight: .black, design: .monospaced))
                                            .foregroundStyle(quest.active ? PipTheme.pale : PipTheme.amberDim)
                                    }
                                }.buttonStyle(.plain)
                                if expandedQuestID == quest.id {
                                    if !quest.objectives.isEmpty {
                                        ForEach(quest.objectives) { objective in
                                            HStack(alignment: .top, spacing: 8) {
                                                Image(systemName: objective.completed ? "checkmark.circle.fill" : objective.failed ? "xmark.circle.fill" : objective.active ? "record.circle" : "circle")
                                                    .foregroundStyle(objective.completed ? PipTheme.muted : PipTheme.amber)
                                                Text(objective.text)
                                                    .font(.system(size: 9, design: .monospaced))
                                                    .foregroundStyle(objective.completed ? PipTheme.muted : PipTheme.pale)
                                                    .strikethrough(objective.completed)
                                                Spacer()
                                            }.padding(.vertical, 3)
                                        }
                                    } else {
                                        Text("NO OBJECTIVE DETAILS IN THIS QUEST RECORD")
                                            .font(.system(size: 8, design: .monospaced)).foregroundStyle(PipTheme.muted)
                                    }
                                    if quest.formID != nil && quest.instance != nil && quest.type != nil {
                                        Button(quest.active ? "DEACTIVATE QUEST MARKER" : "SET ACTIVE QUEST MARKER") {
                                            state.toggleLiveQuest(quest)
                                        }
                                        .font(.system(size: 8, weight: .black, design: .monospaced))
                                        .buttonStyle(.bordered).tint(PipTheme.amber)
                                    }
                                }
                            }
                        }
                    }
                    if state.isLiveData {
                        PipPanel(title: "LIVE DATABASE BROWSER // \\(state.databaseEntries.count) VALUES") {
                            HStack(spacing: 6) {
                                Button("COPY ALL") {
                                    UIPasteboard.general.string = databaseExportText
                                    databaseCopied = true
                                }
                                .font(.system(size: 8, weight: .black, design: .monospaced))
                                .buttonStyle(.bordered).tint(PipTheme.amber)
                                Button("SAVE TXT") { showingDatabaseExporter = true }
                                    .font(.system(size: 8, weight: .black, design: .monospaced))
                                    .buttonStyle(.bordered).tint(PipTheme.amber)
                                Spacer()
                                if databaseCopied {
                                    Text("COPIED").font(.system(size: 8, weight: .bold, design: .monospaced))
                                        .foregroundStyle(PipTheme.amber)
                                }
                            }
                            TextField("SEARCH PATH OR VALUE", text: $databaseSearch)
                                .font(.system(size: 9, design: .monospaced))
                                .padding(8).background(PipTheme.background)
                                .overlay(Rectangle().stroke(PipTheme.amberDim.opacity(0.5)))
                                .foregroundStyle(PipTheme.pale)
                            if databaseSearch.isEmpty {
                                HStack(spacing: 8) {
                                    Button("ROOT") { databaseBrowserPath = "" }
                                        .disabled(databaseBrowserPath.isEmpty)
                                    Button("UP ONE LEVEL") { moveDatabaseBrowserUp() }
                                        .disabled(databaseBrowserPath.isEmpty)
                                    Spacer()
                                    Text(databaseBrowserPath.isEmpty ? "/" : databaseBrowserPath)
                                        .lineLimit(1).truncationMode(.middle)
                                }
                                .font(.system(size: 8, weight: .bold, design: .monospaced))
                                .buttonStyle(.bordered).tint(PipTheme.amber)
                                if visibleDatabaseItems.isEmpty {
                                    Text("NO VALUES AT THIS LEVEL")
                                        .font(.system(size: 9, design: .monospaced)).foregroundStyle(PipTheme.muted)
                                }
                                ForEach(visibleDatabaseItems) { item in
                                    Button {
                                        if item.isFolder { databaseBrowserPath = item.path }
                                    } label: {
                                        HStack(spacing: 7) {
                                            Image(systemName: item.isFolder ? "folder" : "text.alignleft")
                                                .foregroundStyle(PipTheme.amberDim)
                                            VStack(alignment: .leading, spacing: 2) {
                                                Text(item.label.uppercased())
                                                    .font(.system(size: 8, weight: .bold, design: .monospaced))
                                                    .foregroundStyle(PipTheme.pale)
                                                if let value = item.value {
                                                    Text(value).font(.system(size: 8, design: .monospaced))
                                                        .foregroundStyle(PipTheme.muted).lineLimit(2)
                                                }
                                            }
                                            Spacer()
                                            if item.isFolder {
                                                Image(systemName: "chevron.right").font(.system(size: 8, weight: .bold))
                                                    .foregroundStyle(PipTheme.amber)
                                            }
                                        }
                                        .frame(maxWidth: .infinity, alignment: .leading)
                                        .padding(.vertical, 5).contentShape(Rectangle())
                                    }
                                    .buttonStyle(.plain)
                                    Rectangle().fill(PipTheme.amberDim.opacity(0.18)).frame(height: 1)
                                }
                            } else {
                                ForEach(filteredDatabaseEntries) { entry in
                                    VStack(alignment: .leading, spacing: 2) {
                                        Text(entry.path).font(.system(size: 8, weight: .bold, design: .monospaced))
                                            .foregroundStyle(PipTheme.amberDim).textSelection(.enabled)
                                        Text(entry.value).font(.system(size: 9, design: .monospaced))
                                            .foregroundStyle(PipTheme.pale).textSelection(.enabled)
                                    }.frame(maxWidth: .infinity, alignment: .leading)
                                    Rectangle().fill(PipTheme.amberDim.opacity(0.18)).frame(height: 1)
                                }
                            }
                        }
                    }
                    if let status = state.lastActionStatus {
                        Text(status).font(.system(size: 8, weight: .bold, design: .monospaced)).foregroundStyle(PipTheme.amber)
                    }
                }.padding(16)
            }
            .background(PipTheme.background)
            .toolbar(.hidden, for: .navigationBar)
        }
        .fileExporter(
            isPresented: $showingDatabaseExporter,
            document: DatabaseTextDocument(text: databaseExportText),
            contentType: .plainText,
            defaultFilename: "Fallout-London-ATTA-Boy-Data.txt"
        ) { result in
            if case .failure(let error) = result {
                state.lastActionStatus = "DATA EXPORT FAILED · \\(error.localizedDescription)"
            }
        }
    }
}
