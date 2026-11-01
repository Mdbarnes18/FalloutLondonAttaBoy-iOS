# Audit fixes (patch set 1)

These changes were prepared by source review. Swift and Kotlin have not been compiled or run against a live game. The Python reference decoder and 17 synthetic golden fixtures are the only locally executed checks. GitHub Actions must validate the native code.

## Bugs addressed

- Android/Desktop discovery now uses the UDP reply's source address; the reply JSON has no IP field. `IsBusy: true` is surfaced as a refusal.
- Android/Desktop manual IP reconnect retains the manually entered host.
- Android/Desktop decoders recognize handshake (type 1) and busy/refused (type 2) packets.
- Android/Desktop protocol tests cover handshake, refusal, malformed data, local maps, object deltas and graph updates.
- iOS discovery attempts broadcast without making broadcast failure fatal, then unicasts the request across each local /24 subnet.
- iOS remembers the last manual host.
- iOS connection-state and packet events use one ordered stream to prevent first-packet state races.
- iOS UI refreshes are coalesced; database browser rebuilds are throttled.
- Auto-Stimpak is rate-limited, waits for HP to increase between automatic uses, and disables itself after a failed use.
- Fast Travel and Radio RPCs are gated behind an Experimental Commands toggle until their arguments are verified.

## Added

- iOS unit tests under `Tests/AttaBoyTests`.
- 17 synthetic shared fixtures and an independent Python reference decoder under `Shared/`.
- iOS CI fixture verification and simulator tests. The simulator test step is temporarily `continue-on-error`; remove that once it has passed on CI.
- Discovery source-address clarification in `Documentation/PROTOCOL.md`.

## Deliberately unchanged

- `VERSION`, release workflow, icon-fetch steps and Windows/Linux packaging.
- Local-map decoding still assumes exactly width × height pixel bytes; this is not proven by a Fallout: London capture.
- Quest, map-marker and item RPC argument orders remain unverified.
- Android and Desktop protocol sources remain duplicated until they can be built and validated.

The next integration requirement is a real Fallout: London capture. Synthetic fixtures validate decoder logic, not live-game compatibility.
