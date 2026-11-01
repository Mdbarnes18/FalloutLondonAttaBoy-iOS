import Foundation
import Network
import Darwin

final class ConnectionService {
    var onStateChange: ((ConnectionState) -> Void)?
    var onUpdate: ((PipboyUpdate) -> Void)?

    private let queue = DispatchQueue(label: "com.coagulantchip.attaboy.network")
    private var connection: NWConnection?
    private var receiveBuffer = Data()
    private var nextRPCID: UInt32 = 1
    private var heartbeatTimer: DispatchSourceTimer?
    private var reconnectWork: DispatchWorkItem?
    private var discoveryTimeout: DispatchWorkItem?
    private var discoverySource: DispatchSourceRead?
    private var discoverySocket: Int32 = -1
    private var reconnectAttempt = 0
    private var manualHost: String?
    private var manualDisconnect = false
    private var lastReceive = Date()
    private var lastKeepAliveSent = Date()

    func discoverAndConnect() {
        queue.async { [weak self] in
            guard let self else { return }
            self.manualDisconnect = false
            self.reconnectWork?.cancel()
            self.reconnectWork = nil
            self.reconnectAttempt = 0
            self.manualHost = nil
            self.startDiscovery()
        }
    }

    func connect(host: String) {
        queue.async { [weak self] in
            guard let self else { return }
            self.manualDisconnect = false
            self.reconnectWork?.cancel()
            self.reconnectWork = nil
            self.reconnectAttempt = 0
            self.manualHost = host
            self.stopDiscovery()
            self.connectInternal(host: host)
        }
    }

    func disconnect() {
        queue.async { [weak self] in
            guard let self else { return }
            self.manualDisconnect = true
            self.reconnectWork?.cancel()
            self.reconnectWork = nil
            self.stopDiscovery()
            self.stopHeartbeat()
            self.connection?.cancel()
            self.connection = nil
            self.receiveBuffer.removeAll(keepingCapacity: true)
            self.onStateChange?(.disconnected)
        }
    }

    func sendRPC(type: Int, args: [Any]) {
        queue.async { [weak self] in
            guard let self, let connection = self.connection else { return }
            let payload: [String: Any] = ["id": self.nextRPCID, "type": type, "args": args]
            self.nextRPCID &+= 1
            guard JSONSerialization.isValidJSONObject(payload),
                  let json = try? JSONSerialization.data(withJSONObject: payload) else { return }
            self.sendFrame(type: 5, payload: json, over: connection)
        }
    }

    private func startDiscovery() {
        guard !manualDisconnect else { return }
        stopDiscovery()
        connection?.cancel()
        connection = nil
        onStateChange?(.discovering)

        let fd = Darwin.socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        guard fd >= 0 else {
            failAndScheduleReconnect("Could not create UDP discovery socket")
            return
        }

        var enabled: Int32 = 1
        guard Darwin.setsockopt(fd, SOL_SOCKET, SO_BROADCAST, &enabled, socklen_t(MemoryLayout<Int32>.size)) == 0 else {
            Darwin.close(fd)
            failAndScheduleReconnect("Could not enable UDP broadcast")
            return
        }

        var local = sockaddr_in()
        local.sin_len = UInt8(MemoryLayout<sockaddr_in>.size)
        local.sin_family = sa_family_t(AF_INET)
        local.sin_port = 0
        local.sin_addr = in_addr(s_addr: in_addr_t(0))
        let bindResult = withUnsafePointer(to: &local) { pointer in
            pointer.withMemoryRebound(to: sockaddr.self, capacity: 1) {
                Darwin.bind(fd, $0, socklen_t(MemoryLayout<sockaddr_in>.size))
            }
        }
        guard bindResult == 0 else {
            Darwin.close(fd)
            failAndScheduleReconnect("Could not bind UDP discovery socket")
            return
        }

        discoverySocket = fd
        let source = DispatchSource.makeReadSource(fileDescriptor: fd, queue: queue)
        source.setEventHandler { [weak self] in self?.receiveDiscoveryResponse() }
        source.setCancelHandler { Darwin.close(fd) }
        discoverySource = source
        source.resume()

        var destination = sockaddr_in()
        destination.sin_len = UInt8(MemoryLayout<sockaddr_in>.size)
        destination.sin_family = sa_family_t(AF_INET)
        destination.sin_port = UInt16(28000).bigEndian
        destination.sin_addr = in_addr(s_addr: inet_addr("255.255.255.255"))

        let payload = Data(#"{"cmd":"autodiscover"}"#.utf8)
        let sent = payload.withUnsafeBytes { bytes in
            withUnsafePointer(to: &destination) { pointer in
                pointer.withMemoryRebound(to: sockaddr.self, capacity: 1) {
                    Darwin.sendto(fd, bytes.baseAddress, bytes.count, 0, $0, socklen_t(MemoryLayout<sockaddr_in>.size))
                }
            }
        }
        guard sent == payload.count else {
            stopDiscovery()
            failAndScheduleReconnect("Could not send UDP discovery broadcast")
            return
        }

        let timeout = DispatchWorkItem { [weak self] in
            guard let self, self.discoverySocket == fd else { return }
            self.stopDiscovery()
            self.failAndScheduleReconnect("No Fallout game answered UDP discovery on port 28000")
        }
        discoveryTimeout = timeout
        queue.asyncAfter(deadline: .now() + 5, execute: timeout)
    }

    private func receiveDiscoveryResponse() {
        guard discoverySocket >= 0 else { return }
        var sourceAddress = sockaddr_in()
        var addressLength = socklen_t(MemoryLayout<sockaddr_in>.size)
        var buffer = [UInt8](repeating: 0, count: 4096)
        let received = buffer.withUnsafeMutableBytes { bytes in
            withUnsafeMutablePointer(to: &sourceAddress) { pointer in
                pointer.withMemoryRebound(to: sockaddr.self, capacity: 1) {
                    Darwin.recvfrom(discoverySocket, bytes.baseAddress, bytes.count, 0, $0, &addressLength)
                }
            }
        }
        guard received > 0 else { return }

        let data = Data(buffer.prefix(received))
        guard let response = try? JSONSerialization.jsonObject(with: data) as? [String: Any] else { return }
        if response["IsBusy"] as? Bool == true {
            stopDiscovery()
            onStateChange?(.failed("Fallout is already connected to another companion"))
            return
        }
        guard response["MachineType"] is String else { return }

        var address = sourceAddress.sin_addr
        guard let addressText = inet_ntoa(address) else { return }
        let host = String(cString: addressText)
        stopDiscovery()
        reconnectAttempt = 0
        connectInternal(host: host)
    }

    private func stopDiscovery() {
        discoveryTimeout?.cancel()
        discoveryTimeout = nil
        if let source = discoverySource {
            discoverySource = nil
            discoverySocket = -1
            source.cancel()
        } else if discoverySocket >= 0 {
            let fd = discoverySocket
            discoverySocket = -1
            Darwin.close(fd)
        }
    }

    private func connectInternal(host: String) {
        guard !manualDisconnect else { return }
        stopHeartbeat()
        connection?.cancel()
        receiveBuffer.removeAll(keepingCapacity: true)
        onStateChange?(.connecting)

        let parameters = NWParameters.tcp
        parameters.allowLocalEndpointReuse = true
        let tcp = NWConnection(host: NWEndpoint.Host(host), port: 27000, using: parameters)
        connection = tcp

        tcp.stateUpdateHandler = { [weak self] state in
            guard let self, self.connection === tcp else { return }
            switch state {
            case .ready:
                self.reconnectAttempt = 0
                self.lastReceive = Date()
                self.onStateChange?(.connected)
                self.startHeartbeat()
                self.receiveLoop(for: tcp)
            case .waiting:
                self.onStateChange?(.reconnecting)
            case .failed(let error):
                self.stopHeartbeat()
                self.failAndScheduleReconnect(error.localizedDescription)
            case .cancelled:
                self.stopHeartbeat()
                if !self.manualDisconnect { self.scheduleReconnect(reason: "Connection closed") }
                else { self.onStateChange?(.disconnected) }
            default:
                break
            }
        }
        tcp.start(queue: queue)
    }

    private func receiveLoop(for tcp: NWConnection) {
        tcp.receive(minimumIncompleteLength: 1, maximumLength: 64 * 1024) { [weak self] data, _, isComplete, error in
            guard let self, self.connection === tcp else { return }
            if let data, !data.isEmpty {
                self.lastReceive = Date()
                self.receiveBuffer.append(data)
                self.decodeFrames(using: tcp)
            }
            if !isComplete && error == nil {
                self.receiveLoop(for: tcp)
            } else if !self.manualDisconnect {
                self.stopHeartbeat()
                self.scheduleReconnect(reason: error?.localizedDescription ?? "Connection closed")
            }
        }
    }

    private func decodeFrames(using tcp: NWConnection) {
        while receiveBuffer.count >= 5 {
            let size = receiveBuffer.withUnsafeBytes { raw in
                UInt32(littleEndian: raw.loadUnaligned(as: UInt32.self))
            }
            guard size <= 16 * 1024 * 1024 else {
                tcp.cancel()
                failAndScheduleReconnect("Invalid packet size")
                return
            }
            let total = 5 + Int(size)
            guard receiveBuffer.count >= total else { return }

            let type = receiveBuffer[4]
            let payload = receiveBuffer.subdata(in: 5..<total)
            receiveBuffer.removeSubrange(0..<total)

            if type == 0 {
                // The game expects the client to echo a keep-alive when one arrives.
                sendFrame(type: 0, payload: Data(), over: tcp)
                lastKeepAliveSent = Date()
            } else {
                onUpdate?(PipboyPacketDecoder.decode(type: type, payload: payload))
                // Match the reference client: after ordinary traffic, send a keep-alive
                // only when more than two seconds have elapsed since the last one.
                if Date().timeIntervalSince(lastKeepAliveSent) > 2 {
                    sendFrame(type: 0, payload: Data(), over: tcp)
                    lastKeepAliveSent = Date()
                }
            }
        }
    }

    private func sendFrame(type: UInt8, payload: Data, over tcp: NWConnection) {
        var size = UInt32(payload.count).littleEndian
        var packet = Data(bytes: &size, count: 4)
        packet.append(type)
        packet.append(payload)
        tcp.send(content: packet, completion: .contentProcessed { [weak self] error in
            guard let self, let error, !self.manualDisconnect else { return }
            self.failAndScheduleReconnect(error.localizedDescription)
        })
    }

    private func startHeartbeat() {
        stopHeartbeat()
        let timer = DispatchSource.makeTimerSource(queue: queue)
        timer.schedule(deadline: .now() + 20, repeating: 20)
        timer.setEventHandler { [weak self] in
            guard let self, let tcp = self.connection, !self.manualDisconnect else { return }
            if Date().timeIntervalSince(self.lastReceive) > 60 {
                tcp.cancel()
                self.failAndScheduleReconnect("Heartbeat timeout")
                return
            }
        }
        heartbeatTimer = timer
        timer.resume()
    }

    private func stopHeartbeat() {
        heartbeatTimer?.cancel()
        heartbeatTimer = nil
    }

    private func failAndScheduleReconnect(_ reason: String) {
        stopHeartbeat()
        onStateChange?(.failed(reason))
        scheduleReconnect(reason: reason)
    }

    private func scheduleReconnect(reason: String) {
        guard !manualDisconnect, reconnectWork == nil else { return }
        reconnectAttempt += 1
        let delay = min(pow(2.0, Double(min(reconnectAttempt - 1, 5))), 30.0)
        onStateChange?(.reconnecting)
        let work = DispatchWorkItem { [weak self] in
            guard let self, !self.manualDisconnect else { return }
            self.reconnectWork = nil
            if let host = self.manualHost { self.connectInternal(host: host) }
            else { self.startDiscovery() }
        }
        reconnectWork = work
        queue.asyncAfter(deadline: .now() + delay, execute: work)
    }
}
