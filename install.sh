#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
PYTHON_BIN="${PYTHON:-python3}"
VERSION=$(cat "$ROOT/VERSION")
WHEEL=$(find "$ROOT/dist" -maxdepth 1 -type f -name "tardisha-${VERSION}-*.whl" | sort | head -n 1)

if [ -n "$WHEEL" ]; then
  TARGET="$WHEEL"
else
  TARGET="$ROOT"
fi

if "$PYTHON_BIN" -c 'import sys; raise SystemExit(0 if sys.prefix != sys.base_prefix else 1)'; then
  "$PYTHON_BIN" -m pip install --upgrade "$TARGET"
else
  "$PYTHON_BIN" -m pip install --user --upgrade "$TARGET"
fi

echo "Installed TardiSHA ${VERSION} with pip."
echo "Commands: grimchain, tardisha, TardiSHA"
