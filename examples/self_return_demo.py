#!/usr/bin/env python3
from __future__ import annotations
import shutil
import subprocess
import tempfile
from pathlib import Path

command = shutil.which("grimchain")
if command is None:
    local = Path(__file__).resolve().parents[1] / "grimchain"
    command = str(local)

with tempfile.TemporaryDirectory() as td:
    source = Path(td) / "source.txt"
    initial = b"The path out is the path back.\n"
    source.write_bytes(initial)

    first = subprocess.run([command, str(source)], check=True, capture_output=True, text=True).stdout.rstrip("\n")
    source.write_bytes(initial + first.encode("utf-8") + b"\n")
    second = subprocess.run([command, str(source)], check=True, capture_output=True, text=True).stdout.rstrip("\n")

    print("first :", first)
    print("second:", second)
    print("equal :", first == second)
    raise SystemExit(0 if first == second else 1)
