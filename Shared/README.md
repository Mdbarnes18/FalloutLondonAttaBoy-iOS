# Shared Project Contract

This directory records behavior that must remain consistent across native iOS, Android, Windows and Linux clients.

## Shared contract

- Discovery and connection behavior.
- Packet framing and message types.
- Binary database/object graph semantics.
- Local-map packet semantics.
- RPC command definitions and argument ordering.
- Fallout: London data vocabulary verified from captures.
- Player, inventory, quest, map and radio data models.
- Demo/test data and protocol captures.
- Requirement and verification status.

Platform-specific UI, networking APIs, lifecycle handling, audio, haptics, file export and rendering remain native. The SwiftUI iOS implementation is the primary protocol reference; Android and desktop are parallel Kotlin implementations and must be checked against the same contract.
