# Pip-Boy companion protocol: verified baseline and implementation gaps

This document separates the reverse-engineered Fallout 4 companion wire format from Fallout: London-specific behavior. The wire format is a compatibility baseline, not proof that every command or data path works in Fallout: London.

## Primary references

- [PyPipboy](https://github.com/matzman666/PyPipboy) — reference client for discovery, TCP connection handling, keep-alive behavior, binary updates, local-map updates and RPC.
- [Pipboy protocol specification](https://github.com/mattbaker/pipboyspec) — human-readable discovery and communication specification.
- [pipboylib](https://github.com/RobCoIndustries/pipboylib) — independent implementation of framing, message channels, binary database decoding and command IDs.
- [PipBoy protocol exploration](https://github.com/NimVek/pipboy) — independent protocol implementation and packet investigation.
- [MrPippy](https://github.com/ekimekim/mrpippy) — independent Python encode/decode and data-management implementation.

These projects are independent reverse-engineering references. Their agreement is useful evidence, but none alone proves compatibility with every Fallout 4 runtime or Fallout: London installation. See [REFERENCE_SOURCES.md](REFERENCE_SOURCES.md) for source scope and audit notes.

## Transport and message framing

- PC/PS4 UDP discovery: port 28000, JSON request `{"cmd":"autodiscover"}`.
- TCP companion connection: port 27000.
- TCP frame: little-endian UInt32 payload length, UInt8 message type, then exactly that many payload bytes.
- Type 0: heartbeat; the reference behavior echoes a server heartbeat and sends a client heartbeat after ordinary traffic only when its keep-alive timer has expired.
- Type 1: connection handshake JSON (includes host language and version).
- Type 2: busy / connection refused.
- Type 3: incremental binary database update.
- Type 4: local-map update.
- Type 5: JSON RPC command request.
- Type 6: JSON command response.

The reference implementation's heartbeat policy is not a fixed unconditional timer: PyPipboy echoes received heartbeats and otherwise sends a keep-alive after a period without one. Validate any alternative cadence against actual game behavior.

Xbox discovery is documented separately as UDP/5050 with a different, incompletely understood request format. This project currently targets PC/LAN discovery; do not imply Xbox discovery support.

## Type 3 database records

Each record begins with UInt8 value type and little-endian UInt32 node ID.

| Value type | Meaning | Payload |
|---:|---|---|
| 0 | Boolean | UInt8 |
| 1 | Int8 | Int8 |
| 2 | UInt8 | UInt8 |
| 3 | Int32 | Int32 |
| 4 | UInt32 | UInt32 |
| 5 | Float | Float32 |
| 6 | String | NUL-terminated UTF-8 bytes |
| 7 | Array | UInt16 count, then UInt32 node IDs |
| 8 | Object delta | UInt16 additions; each is UInt32 node ID + NUL-terminated key; UInt16 removals; then UInt32 node IDs |

Object updates are deltas. Additions map a key to an existing node ID; removals remove any object key currently pointing to the listed node ID. A parser must reject or report truncated records rather than silently treating a partial update as a complete update. The independent references do not define a type-9 null record; do not assume one is valid without capture evidence.

The object graph is incremental. Node IDs may be referenced before their value record arrives in the same update stream, and save changes can invalidate parts of the tree. Data consumers must tolerate missing paths and re-resolve references when parent objects are replaced.

## Type 4 local map

The reference layout is:

- UInt32 width
- UInt32 height
- Float32 north-west X/Y
- Float32 north-east X/Y
- Float32 south-west X/Y
- remaining pixel bytes

The pixel payload and dimensions must be validated together before rendering. A decoded map packet is not a curated Fallout: London world map.

## Type 5 RPC

The request is JSON with incrementing request ID, command type, and argument array, for example `{"id":3,"type":1,"args":[...]}`. Argument order and value types are command-specific.

Known command IDs in the independent references:

| ID | Command |
|---:|---|
| 0 | UseItem |
| 1 | DropItem |
| 2 | SetFavorite |
| 3 | ToggleComponentFavorite / tag component |
| 4 | SortInventory |
| 5 | ToggleQuestActive |
| 6 | SetCustomMapMarker |
| 7 | RemoveCustomMapMarker |
| 8 | CheckFastTravel |
| 9 | FastTravel |
| 10 | MoveLocalMap |
| 11 | ZoomLocalMap |
| 12 | ToggleRadioStation |
| 13 | RequestLocalMapSnapshot / toggle local-map updates |
| 14 | ClearIdle |

The table identifies command names only. Never enable an action solely because its numeric ID is known. Verify argument order, handle/version semantics, response behavior and Fallout: London applicability before exposing it in the UI. Command responses are not guaranteed for every command.

## Current implementation verification boundary

- Kotlin Android and desktop protocol contract tests cover selected decoder and object-graph cases. They are unit tests, not captured-session integration tests.
- iOS, Android and desktop still require a shared fixture suite built from legally obtained, user-supplied or independently documented packet captures.
- Handshake validation, busy response handling, malformed-record error reporting, complete map-pixel validation, RPC response correlation, and live reconnect behavior must be verified against the reference implementations and a real game session.
- Fallout: London paths, item IDs, quest structures, radio state and map coordinates must come from actual London data captures. Fallout 4 examples are not proof of London data shape.
