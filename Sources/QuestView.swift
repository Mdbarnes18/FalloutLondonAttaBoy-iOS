import SwiftUI

struct QuestView: View {
    @EnvironmentObject private var state: AttaBoyState
    private var remaining: [Quest] { Quest.all.filter { !state.completedQuestIDs.contains($0.id) } }
    private var completed: [Quest] { Quest.all.filter { state.completedQuestIDs.contains($0.id) } }

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 15) {
                    ScreenHeader(title: "QUEST DATA", subtitle: "OBJECTIVES & FIELD NOTES")
                    PipPanel(title: "PROGRESS") {
                        HStack {
                            Text("\(state.completedQuestCount) / \(Quest.all.count) OBJECTIVES COMPLETE").font(.system(size: 11, weight: .bold, design: .monospaced)).foregroundStyle(PipTheme.pale)
                            Spacer()
                            Text("\(Int(Double(state.completedQuestCount) / Double(Quest.all.count) * 100))%").font(.system(size: 15, weight: .black, design: .monospaced)).foregroundStyle(PipTheme.amber)
                        }
                        MeterRow(title: "COMPLETION", value: Int(Double(state.completedQuestCount) / Double(Quest.all.count) * 100))
                    }
                    if !remaining.isEmpty {
                        PipPanel(title: "ACTIVE OBJECTIVES") {
                            ForEach(remaining) { quest in questRow(quest, isComplete: false) }
                        }
                    }
                    if !completed.isEmpty {
                        PipPanel(title: "COMPLETED") {
                            ForEach(completed) { quest in questRow(quest, isComplete: true) }
                        }
                    }
                    Text("QUEST PROGRESS IS STORED LOCALLY ON THIS DEVICE")
                        .font(.system(size: 8, weight: .medium, design: .monospaced)).foregroundStyle(PipTheme.muted)
                }
                .padding(16)
            }
            .background(PipTheme.background)
            .toolbar(.hidden, for: .navigationBar)
        }
    }

    private func questRow(_ quest: Quest, isComplete: Bool) -> some View {
        Button {
            state.toggleQuest(quest)
        } label: {
            HStack(alignment: .top, spacing: 11) {
                Image(systemName: isComplete ? "checkmark.circle.fill" : "circle")
                    .font(.system(size: 20)).foregroundStyle(isComplete ? PipTheme.amberDim : PipTheme.amber)
                VStack(alignment: .leading, spacing: 5) {
                    Text(quest.title).font(.system(size: 12, weight: .black, design: .monospaced))
                        .strikethrough(isComplete).foregroundStyle(isComplete ? PipTheme.muted : PipTheme.pale)
                    Text(quest.location).font(.system(size: 8, weight: .bold, design: .monospaced)).foregroundStyle(PipTheme.amberDim)
                    Text(quest.detail).font(.system(size: 10, design: .monospaced)).foregroundStyle(PipTheme.muted).multilineTextAlignment(.leading)
                }
                Spacer(minLength: 0)
            }
            .padding(.vertical, 8)
            .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
    }
}
