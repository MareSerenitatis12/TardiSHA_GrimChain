#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from TardiSHA.domus_stream import living_domus_for_source

ROOT_FILES = (
    ".gitignore", "LICENSE", "README.md", "COMMANDS.md", "VERSION",
    "CHANGELOG.md", "CITATION.cff", "CONTRIBUTING.md", "COPYRIGHT",
    "DICTIONARY.md", "ORIGIN.md", "QUICKSTART.md", "RELEASE_CONTENTS.md",
    "SECURITY.md", "TRADEMARKS.md", "TardiSHA_selftest.py", "grimchain",
    "tardisha", "install.sh", "setup.py", "pyproject.toml", "MANIFEST.in",
    "The Birth of Metal Through Fire and Breath.pdf",
)


def selected() -> list[Path]:
    result = [ROOT / name for name in ROOT_FILES]
    result.extend(sorted(path for path in (ROOT / "TardiSHA").glob("*.py")))
    result.extend(sorted(path for path in (ROOT / "TardiSHA").glob("*.c")))
    for directory in ("docs", "examples", "packaging", "validation"):
        for path in sorted((ROOT / directory).rglob("*")):
            if not path.is_file():
                continue
            if "results" in path.parts or "__pycache__" in path.parts:
                continue
            if path.suffix in {".pyc", ".so"}:
                continue
            result.append(path)
    unique = {path.resolve(): path for path in result if path.exists()}
    return sorted(unique.values(), key=lambda item: item.relative_to(ROOT).as_posix())


files = selected()
entries = [
    {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": path.stat().st_size,
        "grimchain": living_domus_for_source(path, 0, kind="file"),
    }
    for path in files
]
body = {"format": 2, "proof": "verified depth-zero Grimchain", "files": len(entries), "entries": entries}
(ROOT / "SOURCE_GRIMCHAIN_MANIFEST.json").write_text(
    json.dumps(body, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps({"source_manifest": "SOURCE_GRIMCHAIN_MANIFEST.json", "files": len(entries)}, indent=2))
