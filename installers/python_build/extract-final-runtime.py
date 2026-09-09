#!/usr/bin/env python3
"""Extract the finalized TardiSHA build source from the immutable preservation notebook."""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path


def payload_bytes(cell: dict) -> bytes:
    meta = cell.get("metadata", {})
    if meta.get("tardisha_binary_attachment"):
        source_path = meta["tardisha_source_path"]
        attachment = cell.get("attachments", {}).get(source_path, {})
        encoded = attachment.get("application/octet-stream")
        if not encoded:
            raise ValueError(f"missing binary attachment for {source_path}")
        return base64.b64decode(encoded)
    encoding = meta.get("tardisha_encoding", "utf-8")
    source = cell.get("source", "")
    if isinstance(source, list):
        source = "".join(source)
    return source.encode(encoding)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("notebook", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()

    notebook_bytes = args.notebook.read_bytes()
    notebook = json.loads(notebook_bytes.decode("utf-8"))
    target = args.destination / "TardiSHA"
    target.mkdir(parents=True, exist_ok=True)

    checked = 0
    written = 0
    for cell in notebook.get("cells", []):
        meta = cell.get("metadata", {})
        source_path = meta.get("tardisha_source_path")
        expected = meta.get("tardisha_sha256")
        expected_bytes = meta.get("tardisha_bytes")
        if not source_path or not expected:
            continue
        body = payload_bytes(cell)
        checked += 1
        actual = hashlib.sha256(body).hexdigest()
        if actual != expected or len(body) != expected_bytes:
            raise ValueError(f"preservation metadata mismatch: {source_path}")
        if source_path.endswith(".py") or source_path == "_alqc_kernel.c":
            (target / source_path).write_bytes(body)
            written += 1

    if written != 29:
        raise ValueError(f"expected 29 runtime source bodies, got {written}")
    print(f"notebook_sha256={hashlib.sha256(notebook_bytes).hexdigest()}")
    print(f"payloads_checked={checked}")
    print(f"runtime_sources_written={written}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
