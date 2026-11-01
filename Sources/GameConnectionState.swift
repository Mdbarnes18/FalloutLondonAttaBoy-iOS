import Foundation

enum ConnectionState: Equatable {
    case disconnected
    case discovering
    case connecting
    case connected
    case reconnecting
    case failed(String)
}
