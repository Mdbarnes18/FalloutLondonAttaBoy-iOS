#!/usr/bin/env bash
set -euo pipefail

# Import the complete ATTA-Boy asset pack without flattening, recompressing,
# renaming, or dropping platform variants. Run from any directory.
#
# Usage:
#   ./scripts/import-complete-asset-pack.sh /path/to/ATTA-Boy-Complete-Asset-Pack.zip
#
# The archive is copied into Assets/Source/ATTA-Boy-Complete-Asset-Pack.
# A SHA-256 inventory is written beside it. Existing files are never silently
# overwritten; use --replace only when intentionally refreshing the import.

REPLACE=0
if [[ "${1:-}" == "--replace" ]]; then
  REPLACE=1
  shift
fi

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 [--replace] /path/to/ATTA-Boy-Complete-Asset-Pack.zip" >&2
  exit 2
fi

ARCHIVE="$(realpath "$1")"
ROOT="$(git rev-parse --show-toplevel)"
DEST="$ROOT/Assets/Source/ATTA-Boy-Complete-Asset-Pack"

[[ -f "$ARCHIVE" ]] || { echo "Archive not found: $ARCHIVE" >&2; exit 2; }
command -v python3 >/dev/null || { echo "python3 is required" >&2; exit 2; }

if [[ -e "$DEST" && "$REPLACE" -ne 1 ]]; then
  echo "Destination already exists: $DEST" >&2
  echo "Review it or rerun with --replace to refresh the import." >&2
  exit 3
fi

python3 - "$ARCHIVE" "$DEST" "$REPLACE" <<'PY'
import hashlib, json, pathlib, shutil, sys, zipfile

archive = pathlib.Path(sys.argv[1])
dest = pathlib.Path(sys.argv[2])
replace = sys.argv[3] == "1"

with zipfile.ZipFile(archive) as zf:
    members = [m for m in zf.infolist() if not m.is_dir()]
    if not members:
        raise SystemExit("Archive contains no files.")

    # Validate every path before extracting anything. Reject absolute paths,
    # parent traversal, and symlinks to prevent writing outside the repo.
    root_name = dest.parent.resolve()
    for member in members:
        name = member.filename.replace("\\", "/")
        path = pathlib.PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts or not path.parts:
            raise SystemExit(f"Unsafe archive path: {member.filename}")
        mode = (member.external_attr >> 16) & 0o170000
        if mode == 0o120000:
            raise SystemExit(f"Symlink entry not permitted: {member.filename}")

    if dest.exists():
        if not replace:
            raise SystemExit(f"Destination exists: {dest}")
        shutil.rmtree(dest)
    dest.mkdir(parents=True, exist_ok=True)

    inventory = []
    total = 0
    for member in members:
        relative = pathlib.PurePosixPath(member.filename.replace("\\", "/"))
        target = dest.joinpath(*relative.parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        digest = hashlib.sha256()
        size = 0
        with zf.open(member, "r") as src, target.open("wb") as out:
            while True:
                chunk = src.read(1024 * 1024)
                if not chunk:
                    break
                out.write(chunk)
                digest.update(chunk)
                size += len(chunk)
        total += size
        inventory.append({
            "path": relative.as_posix(),
            "size_bytes": size,
            "sha256": digest.hexdigest()
        })

manifest = {
    "source_archive": archive.name,
    "file_count": len(inventory),
    "total_uncompressed_bytes": total,
    "files": sorted(inventory, key=lambda item: item["path"].casefold())
}
(dest / "ASSET-MANIFEST.json").write_text(
    json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
)
print(f"Imported {len(inventory):,} files ({total:,} bytes) to {dest}")
print(f"Manifest: {dest / 'ASSET-MANIFEST.json'}")
PY

echo
echo "Import complete. Review the asset manifest, then stage the imported folder:"
echo "  git add Assets/Source/ATTA-Boy-Complete-Asset-Pack"
echo "  git status --short"
