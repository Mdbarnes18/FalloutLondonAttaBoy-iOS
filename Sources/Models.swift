import Foundation

enum AppTab: String, CaseIterable, Identifiable {
    case status, map, inventory, radio, quests
    var id: String { rawValue }
    var title: String {
        switch self {
        case .status: "STATUS"
        case .map: "MAP"
        case .inventory: "ITEMS"
        case .radio: "RADIO"
        case .quests: "DATA"
        }
    }
    var symbol: String {
        switch self {
        case .status: "waveform.path.ecg"
        case .map: "map"
        case .inventory: "backpack"
        case .radio: "dot.radiowaves.left.and.right"
        case .quests: "text.book.closed"
        }
    }
}

struct SpecialStat: Identifiable {
    let name: String
    let value: Int
    var id: String { name }
    static let all: [SpecialStat] = [
        .init(name: "STR", value: 5), .init(name: "PER", value: 7),
        .init(name: "END", value: 6), .init(name: "CHA", value: 4),
        .init(name: "INT", value: 8), .init(name: "AGI", value: 6),
        .init(name: "LCK", value: 5)
    ]
}

enum ItemCategory: String, CaseIterable, Identifiable {
    case all = "ALL", weapons = "WEAPONS", apparel = "APPAREL", aid = "AID", misc = "MISC"
    var id: String { rawValue }
}

struct InventoryItem: Identifiable {
    let id: String
    let name: String
    let detail: String
    let category: ItemCategory
    let weight: Double
    let value: Int
    let symbol: String
    static let samples: [InventoryItem] = [
        .init(id: "service-rifle", name: "SERVICE RIFLE", detail: "Well-worn · .303", category: .weapons, weight: 8.0, value: 85, symbol: "scope"),
        .init(id: "balisong", name: "BLADE", detail: "A little too familiar", category: .weapons, weight: 1.0, value: 22, symbol: "dagger"),
        .init(id: "leather-coat", name: "LEATHER COAT", detail: "London weather issue", category: .apparel, weight: 4.0, value: 45, symbol: "tshirt"),
        .init(id: "stimpak", name: "STIMPAK", detail: "Restores health", category: .aid, weight: 0.5, value: 35, symbol: "cross.case"),
        .init(id: "radaway", name: "RADAWAY", detail: "Reduces radiation", category: .aid, weight: 0.5, value: 40, symbol: "pills"),
        .init(id: "ticket", name: "UNDERGROUND TICKET", detail: "Probably expired", category: .misc, weight: 0.1, value: 2, symbol: "ticket")
    ]
}

struct District: Identifiable {
    let id: String
    let name: String
    let subtitle: String
    let x: CGFloat
    let y: CGFloat
    static let all: [District] = [
        .init(id: "islington", name: "ISLINGTON", subtitle: "Northern borough", x: 0.48, y: 0.17),
        .init(id: "camden", name: "CAMDEN", subtitle: "Market district", x: 0.25, y: 0.36),
        .init(id: "city", name: "THE CITY", subtitle: "Financial ruins", x: 0.69, y: 0.42),
        .init(id: "westminster", name: "WESTMINSTER", subtitle: "Political quarter", x: 0.36, y: 0.62),
        .init(id: "lambeth", name: "LAMBETH", subtitle: "South bank", x: 0.69, y: 0.79)
    ]
}

struct RadioStation: Identifiable {
    let id: String
    let name: String
    let frequency: String
    let description: String
    static let all: [RadioStation] = [
        .init(id: "mind", name: "MIND THE GAP", frequency: "98.4", description: "London announcements & curiosities"),
        .init(id: "reich", name: "BRITISH BROADCAST", frequency: "104.2", description: "News from the other side"),
        .init(id: "swing", name: "SWING TIME", frequency: "88.1", description: "A little music for the wasteland")
    ]
}

struct Quest: Identifiable {
    let id: String
    let title: String
    let location: String
    let detail: String
    static let all: [Quest] = [
        .init(id: "first-steps", title: "FIRST STEPS", location: "THAMESHAVEN", detail: "Find your bearings and learn what remains of London."),
        .init(id: "lost-property", title: "LOST PROPERTY", location: "CAMDEN", detail: "Track down a missing parcel for a local trader."),
        .init(id: "power-play", title: "POWER PLAY", location: "THE CITY", detail: "Restore power to a damaged relay station.")
    ]
}
