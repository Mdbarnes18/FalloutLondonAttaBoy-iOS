#!/usr/bin/env python3
"""Independent reference decoder for the synthetic shared Pip-Boy packet fixtures."""
import json
import pathlib
import struct

FIX = pathlib.Path(__file__).resolve().parent.parent / "fixtures" / "packets.json"

def data_records(payload):
    i, out = 0, []
    def take(n):
        nonlocal i
        if i + n > len(payload):
            raise ValueError("truncated")
        result = payload[i:i+n]
        i += n
        return result
    def u8(): return take(1)[0]
    def u16(): return struct.unpack("<H", take(2))[0]
    def u32(): return struct.unpack("<I", take(4))[0]
    def cstr():
        nonlocal i
        end = payload.find(bytes([0]), i)
        if end < 0: raise ValueError("unterminated string")
        value = payload[i:end].decode("utf-8")
        i = end + 1
        return value
    while i < len(payload):
        kind, node = u8(), u32()
        if kind == 0: out.append(["bool", node, bool(u8())])
        elif kind == 1: out.append(["int8", node, struct.unpack("<b", take(1))[0]])
        elif kind == 2: out.append(["uint8", node, u8()])
        elif kind == 3: out.append(["int32", node, struct.unpack("<i", take(4))[0]])
        elif kind == 4: out.append(["uint32", node, u32()])
        elif kind == 5: out.append(["float32", node, struct.unpack("<f", take(4))[0]])
        elif kind == 6: out.append(["string", node, cstr()])
        elif kind == 7: out.append(["array", node, [u32() for _ in range(u16())]])
        elif kind == 8:
            added = [[cstr(), child] for child in []]
            count = u16()
            added = []
            for _ in range(count):
                child = u32()
                added.append([cstr(), child])
            removed = [u32() for _ in range(u16())]
            out.append(["object", node, added, removed])
        else: raise ValueError("unknown value type")
    return out

def decode_map(payload):
    if len(payload) < 32: raise ValueError("truncated map header")
    width, height = struct.unpack_from("<II", payload)
    if not (1 <= width <= 4096 and 1 <= height <= 4096): raise ValueError("invalid dimensions")
    corners = list(struct.unpack_from("<6f", payload, 8))
    pixels = payload[32:]
    if len(pixels) != width * height: raise ValueError("pixel count mismatch")
    return {"width": width, "height": height, "corners": corners, "pixels": list(pixels)}

def main():
    saved = json.loads(FIX.read_text(encoding="utf-8"))["cases"]
    assert len(saved) == 17, f"expected 17 fixtures, got {len(saved)}"
    for case in saved:
        payload = bytes.fromhex(case["payloadHex"])
        try:
            decoded = data_records(payload) if case["packetType"] == 3 else decode_map(payload)
            verdict = "ok"
        except (ValueError, struct.error, UnicodeDecodeError):
            decoded, verdict = None, "reject"
        assert verdict == case["expect"], f'{case["name"]}: expected {case["expect"]}, got {verdict}'
        assert decoded == case["decoded"], f'{case["name"]}: decoded result differs'
    print(f"OK: {len(saved)} synthetic packet fixtures")
if __name__ == "__main__":
    main()
