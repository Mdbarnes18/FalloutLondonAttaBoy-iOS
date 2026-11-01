import SwiftUI

struct QuestView: View {
    @EnvironmentObject private var state: AttaBoyState
    @State private var expandedQuestID: String?

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
                    if let status = state.lastActionStatus {
                        Text(status).font(.system(size: 8, weight: .bold, design: .monospaced)).foregroundStyle(PipTheme.amber)
                    }
                }.padding(16)
            }
            .background(PipTheme.background)
            .toolbar(.hidden, for: .navigationBar)
        }
    }
}
