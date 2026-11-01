# Reference sources and audit register

This register records the upstream material used to understand the Fallout 4 Pip-Boy companion protocol. The projects below are research references; this app does not copy their implementation wholesale.

## Core protocol references

| Source | What it supports | Limits / notes |
|---|---|---|
| [PyPipboy](https://github.com/matzman666/PyPipboy) | UDP autodiscovery, TCP/27000, 5-byte little-endian frame header, handshake/busy handling, keep-alive policy, type-3 record parsing, local-map layout, RPC transport | Reverse-engineered Fallout 4 companion protocol; its README describes the library as alpha. |
| [Pipboy specification](https://github.com/mattbaker/pipboyspec) | Written discovery and communication specification, channel types, record layouts, RPC envelope and documented command arguments | Community-maintained reverse-engineering specification; verify against code and captures. |
| [pipboylib](https://github.com/RobCoIndustries/pipboylib) | Independent constants, channel IDs, command IDs, binary database parser, map parser and examples | JavaScript implementation; useful cross-check, not a Fallout: London guarantee. |
| [NimVek/pipboy](https://github.com/NimVek/pipboy) | Independent protocol implementation and packet investigation | README notes that some platform-specific discovery details remain uncertain. |
| [MrPippy](https://github.com/ekimekim/mrpippy) | Independent Python encoding/decoding and data management | Draws on PyPipboy; useful corroboration, not wholly independent evidence. |

## Additional context

- [PipBoyClient](https://github.com/cpopp/PipBoyClient) documents a minimal discovery, TCP framing, heartbeat and RPC experiment.
- [Pipboy Explorations](https://github.com/mattbaker/pipboy-explorations) records earlier protocol research.
- [Pip-Boy Companion App Enabler (AE)](https://www.nexusmods.com/fallout4/mods/108133) is relevant to modern Fallout 4 runtime availability of the companion service. It is not a protocol specification and is not a Fallout: London compatibility guarantee.

## Source review findings for this repository

1. The current app documentation previously listed ports, packet types and command IDs without linking the reverse-engineering sources. This register and `PROTOCOL.md` now make that provenance explicit.
2. The references agree on PC discovery via UDP/28000, TCP/27000, a five-byte little-endian frame header, message types 0–6, and the type-3 incremental object graph.
3. The reference heartbeat behavior is conditional/echo-based. A fixed periodic heartbeat should not be described as proven equivalent without live testing.
4. The references define type-3 value types 0–8. A type-9 null value is not part of the cited baseline and must not be treated as established protocol behavior.
5. The reference protocol includes connection handshake (type 1) and busy/refusal (type 2). The app must explicitly validate these states rather than treating successful TCP establishment alone as a fully accepted companion session.
6. The references document command IDs, but each RPC's argument semantics and response behavior must be validated before gameplay actions are marked supported.
7. These are Fallout 4 companion protocol references. Fallout: London data paths, IDs, item metadata, quest structures, radio behavior and map geography require London-specific captures or verification.

## Release policy

- Preserve upstream licenses and attribution. Do not copy GPL-licensed code into this repository without a deliberate license-compatibility review.
- Use protocol descriptions and independently written implementations as interoperability references; do not redistribute Bethesda assets, decompiled proprietary code, or private Team FOLON material.
- Record the exact upstream revision and the local test fixture provenance when adding packet fixtures.
- A protocol unit test proves only the behavior asserted by that test. Live-game compatibility requires a real session and repeatable evidence.
