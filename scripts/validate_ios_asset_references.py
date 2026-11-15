#!/usr/bin/env python3
"""Fail CI when a literal SwiftUI image asset name is missing from Assets.xcassets."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "Assets.xcassets"
SOURCES = ROOT / "Sources"

def catalog_names() -> set[str]:
    names: set[str] = set()
    for contents in ASSETS.rglob("Contents.json"):
        try:
            data = json.loads(contents.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"Invalid asset catalog metadata: {contents}: {exc}", file=sys.stderr)
            raise SystemExit(2)
        if contents.parent.name.endswith(".imageset"):
            names.add(contents.parent.name.removesuffix(".imageset"))
        for image in data.get("images", []):
            filename = image.get("filename")
            if filename:
                # The asset's lookup name is the enclosing imageset, not its file name.
                continue
    return names

def main() -> int:
    available = catalog_names()
    missing: list[str] = []
    image_call = re.compile(r'\bImage\s*\(\s*"([^"]+)"')
    label_image = re.compile(r'\bLabel\s*\([^\n]*?\bimage\s*:\s*"([^"]+)"')

    for source in sorted(SOURCES.rglob("*.swift")):
        text = source.read_text(encoding="utf-8")
        for pattern in (image_call, label_image):
            for match in pattern.finditer(text):
                name = match.group(1)
                if name not in available:
                    line = text.count("\n", 0, match.start()) + 1
                    missing.append(f"{source.relative_to(ROOT)}:{line}: {name}")

    if missing:
        print("Missing SwiftUI image assets:")
        print("\n".join(f"  - {item}" for item in missing))
        return 1

    print(f"Verified SwiftUI image references against {len(available)} image sets.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
