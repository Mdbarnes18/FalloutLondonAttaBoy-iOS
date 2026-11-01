import XCTest
@testable import AttaBoy

final class PipboyProtocolTests: XCTestCase {
    func testHandshakeIsDecoded() {
        let payload = Data(#"{"lang":"en","version":"1.11.0"}"#.utf8)
        guard case .connectionAccepted(let handshake) = PipboyPacketDecoder.decode(type: 1, payload: payload) else {
            return XCTFail("Expected handshake")
        }
        XCTAssertEqual(handshake.language, "en")
        XCTAssertEqual(handshake.version, "1.11.0")
    }

    func testBusyReplyIsDecoded() {
        guard case .connectionRefused = PipboyPacketDecoder.decode(type: 2, payload: Data()) else {
            return XCTFail("Expected connection refusal")
        }
    }

    func testUnknownMessageIsPreserved() {
        let payload = Data([1, 2, 3])
        guard case .unknown(let type, let actual) = PipboyPacketDecoder.decode(type: 99, payload: payload) else {
            return XCTFail("Expected unknown message")
        }
        XCTAssertEqual(type, 99)
        XCTAssertEqual(actual, payload)
    }

    func testTruncatedDataPacketIsRejectedAtomically() {
        let payload = Data([0, 7, 0, 0, 0, 1, 3, 1])
        guard case .unknown(let type, _) = PipboyPacketDecoder.decode(type: 3, payload: payload) else {
            return XCTFail("Expected malformed data update")
        }
        XCTAssertEqual(type, 3)
    }

    func testLocalMapRejectsInvalidDimensions() {
        let payload = Data(repeating: 0, count: 32)
        guard case .unknown(let type, _) = PipboyPacketDecoder.decode(type: 4, payload: payload) else {
            return XCTFail("Expected invalid map")
        }
        XCTAssertEqual(type, 4)
    }
}
