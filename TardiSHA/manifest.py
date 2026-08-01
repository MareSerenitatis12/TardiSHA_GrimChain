"""Grimchain file and directory manifests.

The public SOURCE_MANIFEST ledger shape is retained: a name, a file count,
and sorted entries. Each entry carries its Grimchain
value, and the complete entry body receives its own deterministic Grimchain.
"""
from __future__ import annotations

import json
import os
import tempfile
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any

from .domus import living_domus_seal, resolve_domus
from .domus_stream import file_domus_record, living_domus_for_source
from .hashing import TardiSHAError, canonical_emission, validate_middle_length, validate_nonce
from .route import resolve_parents


THIS_FILE_HEADER = "THIS FILE\n"
_THIS_FILE_MARKER = ("\n" + THIS_FILE_HEADER).encode("utf-8")


def default_manifest_name(target: Path, recursive: bool) -> str:
    name = target.name or "root"
    prefix = "manifest-recurse-" if target.is_dir() and recursive else "manifest-"
    return f"{prefix}{name}.grim"


def manifest_output_path(target: Path, output: Path | None, recursive: bool) -> Path:
    default_name = default_manifest_name(target, recursive)
    if output is None:
        return Path.cwd() / default_name
    candidate = output.expanduser()
    if candidate.exists() and candidate.is_dir():
        return candidate / default_name
    return candidate


def _path_witness(path: Path) -> tuple[int, int, int, int, int, int]:
    stat = path.lstat()
    return (
        stat.st_mode,
        stat.st_size,
        stat.st_mtime_ns,
        stat.st_ctime_ns,
        stat.st_dev,
        stat.st_ino,
    )


def _lexical_absolute(path: Path) -> Path:
    return Path(os.path.abspath(os.fspath(path.expanduser())))


def _selected_entries(
    root: Path, recursive: bool, excludes: tuple[Path, ...] = ()
) -> list[tuple[str, Path, str]]:
    excluded = {_lexical_absolute(path) for path in excludes}
    if root.is_file() and not root.is_symlink():
        if _lexical_absolute(root) in excluded:
            raise TardiSHAError("manifest source cannot be excluded from itself")
        return [("file", root, root.name)]
    if not root.is_dir() or root.is_symlink():
        raise TardiSHAError(f"manifest source is not a regular file or directory: {root}")

    selected: list[tuple[str, Path, str]] = [("directory", root, ".")]
    stack = [root]
    while stack:
        current = stack.pop()
        try:
            scanned = sorted(os.scandir(current), key=lambda entry: entry.name)
        except OSError as exc:
            raise TardiSHAError(f"cannot read manifest directory {current}: {exc}") from exc
        directories: list[Path] = []
        for entry in scanned:
            child = Path(entry.path)
            if _lexical_absolute(child) in excluded:
                continue
            relative = child.relative_to(root).as_posix()
            if entry.is_symlink():
                selected.append(("symlink", child, relative))
            elif entry.is_dir(follow_symlinks=False):
                selected.append(("directory", child, relative))
                if recursive:
                    directories.append(child)
            elif entry.is_file(follow_symlinks=False):
                selected.append(("file", child, relative))
            else:
                raise TardiSHAError(f"unsupported manifest entry type: {relative}")
        if recursive:
            stack.extend(reversed(directories))
    return sorted(selected, key=lambda item: item[2])


def _manifest_body_grimchain(
    entries: list[dict[str, Any]], source_witness: dict[str, Any], middle: int, nonce: int
) -> str:
    body = {
        "files": sum(entry["type"] == "file" for entry in entries),
        "entry_count": len(entries),
        "source_witness": source_witness,
        "entries": entries,
    }
    emission, _source = canonical_emission(body)
    g_i, g_j, _witness = resolve_parents(emission)
    resolution = resolve_domus(
        g_i,
        g_j,
        hash_id=emission.source_digest,
        emission=emission,
        source_size=emission.source_size,
        source_domain="canonical",
        nonce=nonce,
    )
    return living_domus_seal(
        resolution,
        middle,
        source_digest=emission.source_digest,
        source_size=emission.source_size,
        source_domain="canonical",
        nonce=nonce,
    )


def _manifest_entry_worker(payload: tuple[str, str, int, int]) -> dict[str, Any]:
    """Return one source-stable regular-file entry."""
    source_text, relative_path, middle, nonce = payload
    source = Path(source_text)
    seal, emission, _route = file_domus_record(source, middle, nonce=nonce)
    return {
        "type": "file",
        "bytes": emission.source_size,
        "path": relative_path,
        "source_digest": emission.source_digest,
        "source_domain": emission.source_domain,
        "grimchain": seal,
    }


def _worker_count(file_count: int) -> int:
    cpu_count = os.cpu_count()
    if cpu_count is None:
        raise TardiSHAError("CPU count is required for parallel manifest construction")
    if isinstance(cpu_count, bool) or not isinstance(cpu_count, int) or cpu_count < 1:
        raise TardiSHAError("CPU count must be a positive integer")
    return min(file_count, cpu_count)


def _nonfile_entry(kind: str, path: Path, relative: str) -> dict[str, Any]:
    before = _path_witness(path)
    if kind == "directory":
        body: dict[str, Any] = {"type": "directory", "path": relative}
    elif kind == "symlink":
        target = os.readlink(path)
        body = {"type": "symlink", "path": relative, "target": target}
    else:
        raise TardiSHAError(f"unsupported manifest entry kind: {kind}")
    after = _path_witness(path)
    if after != before:
        raise TardiSHAError(f"manifest entry changed while witnessed: {relative}")
    return body


def _source_identity_record(entry: dict[str, Any]) -> dict[str, Any]:
    kind = entry["type"]
    if kind == "file":
        return {
            "type": "file",
            "path": entry["path"],
            "digest": entry["source_digest"],
            "size": entry["bytes"],
        }
    if kind == "directory":
        return {"type": "directory", "path": entry["path"]}
    if kind == "symlink":
        return {"type": "symlink", "path": entry["path"], "target": entry["target"]}
    raise TardiSHAError(f"unsupported manifest identity kind: {kind}")


def _build_manifest_pass(
    root: Path,
    *,
    middle: int,
    recursive: bool,
    nonce: int,
    exclusions: tuple[Path, ...],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    selected = _selected_entries(root, recursive, exclusions)
    file_items = [(path, relative) for kind, path, relative in selected if kind == "file"]
    payloads = [(str(path), relative, middle, nonce) for path, relative in file_items]
    if len(payloads) > 1:
        with ProcessPoolExecutor(max_workers=_worker_count(len(payloads))) as pool:
            file_records = list(pool.map(_manifest_entry_worker, payloads))
    else:
        file_records = [_manifest_entry_worker(payload) for payload in payloads]
    files_by_path = {record["path"]: record for record in file_records}

    entries: list[dict[str, Any]] = []
    for kind, path, relative in selected:
        if kind == "file":
            entries.append(files_by_path[relative])
        else:
            entries.append(_nonfile_entry(kind, path, relative))

    source_body = {
        "scope": "recursive" if recursive else "direct",
        "entries": [_source_identity_record(entry) for entry in entries],
    }
    source_emission, _source = canonical_emission(source_body)
    if not source_emission.closure.verifies or source_emission.closure.truth != 1:
        raise RuntimeError("manifest source witness must close with Truth = 1")
    source_witness = json.loads(
        json.dumps(source_emission.as_dict(), ensure_ascii=False, sort_keys=True)
    )
    return entries, source_witness


def build_grimchain_manifest(
    target: str | Path,
    *,
    middle: int,
    recursive: bool = False,
    nonce: int = 0,
    exclude: str | Path | None = None,
    cache: bool = False,
) -> dict[str, Any]:
    if cache:
        raise TardiSHAError("manifest cache use is prohibited; Q0 posture cannot replace Q1 source truth")
    root = Path(target).expanduser().resolve()
    width = validate_middle_length(middle)
    salt = validate_nonce(nonce)
    exclusions = (() if exclude is None else (Path(exclude).expanduser().resolve(),))
    if recursive and not root.is_dir():
        raise TardiSHAError("-R/--recursive requires a directory manifest")

    first_entries, first_witness = _build_manifest_pass(
        root,
        middle=width,
        recursive=recursive,
        nonce=salt,
        exclusions=exclusions,
    )
    second_entries, second_witness = _build_manifest_pass(
        root,
        middle=width,
        recursive=recursive,
        nonce=salt,
        exclusions=exclusions,
    )
    if first_entries != second_entries or first_witness != second_witness:
        raise TardiSHAError("manifest source changed between its two complete temporal witnesses")

    mode = "recursive " if root.is_dir() and recursive else ""
    kind = "directory" if root.is_dir() else "file"
    manifest = {
        "name": f"{root.name or 'root'} {mode}{kind} Grimchain manifest",
        "files": sum(entry["type"] == "file" for entry in first_entries),
        "entry_count": len(first_entries),
        "source_witness": first_witness,
        "entries": first_entries,
    }
    manifest["grimchain"] = _manifest_body_grimchain(
        first_entries, first_witness, width, salt
    )
    return manifest


def _prepared_manifest_bytes(manifest: dict[str, Any]) -> bytes:
    """Render the manifest and its waiting THIS FILE line before self-chaining."""
    body = json.dumps(manifest, ensure_ascii=False, indent=2)
    return (body + "\n" + THIS_FILE_HEADER).encode("utf-8")


def _read_self_returning_manifest(destination: Path) -> tuple[dict[str, Any], str]:
    raw = destination.read_bytes()
    marker_at = raw.rfind(_THIS_FILE_MARKER)
    if marker_at < 0:
        raise ValueError("THIS FILE block is missing")
    terminal = raw[marker_at + len(_THIS_FILE_MARKER):]
    if not terminal.endswith(b"\n"):
        raise ValueError("THIS FILE Grimchain lacks its terminal newline")
    seal_bytes = terminal[:-1]
    if not seal_bytes or b"\n" in seal_bytes or b"\r" in seal_bytes:
        raise ValueError("THIS FILE must contain exactly one Grimchain line")
    stored = json.loads(raw[:marker_at].decode("utf-8"))
    return stored, seal_bytes.decode("utf-8")


def write_grimchain_manifest(
    target: str | Path,
    output: str | Path,
    *,
    middle: int,
    recursive: bool = False,
    nonce: int = 0,
    cache: bool = False,
) -> dict[str, Any]:
    if cache:
        raise TardiSHAError("manifest cache use is prohibited; Q0 posture cannot replace Q1 source truth")
    destination = Path(output).expanduser().resolve()
    width = validate_middle_length(middle)
    salt = validate_nonce(nonce)
    manifest = build_grimchain_manifest(
        target,
        middle=width,
        recursive=recursive,
        nonce=salt,
        exclude=destination,
        cache=cache,
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".part", dir=destination.parent
    )
    temp = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(_prepared_manifest_bytes(manifest))
            handle.flush()
            os.fsync(handle.fileno())

        first = living_domus_for_source(temp, width, kind="file", nonce=salt)
        with temp.open("ab") as handle:
            handle.write(first.encode("utf-8"))
            handle.write(b"\n")
            handle.flush()
            os.fsync(handle.fileno())

        final = living_domus_for_source(temp, width, kind="file", nonce=salt)
        if final != first:
            raise RuntimeError("THIS FILE self-return did not close to the same Grimchain")
        os.replace(temp, destination)
    except Exception:
        temp.unlink(missing_ok=True)
        raise

    manifest["THIS FILE"] = final
    return manifest


def verify_grimchain_manifest(
    target: str | Path,
    manifest_path: str | Path,
    *,
    middle: int,
    recursive: bool = False,
    nonce: int = 0,
    cache: bool = False,
) -> bool:
    if cache:
        return False
    destination = Path(manifest_path).expanduser().resolve()
    try:
        width = validate_middle_length(middle)
        salt = validate_nonce(nonce)
        stored, stored_self = _read_self_returning_manifest(destination)
        expected = build_grimchain_manifest(
            target,
            middle=width,
            recursive=recursive,
            nonce=salt,
            exclude=destination,
            cache=cache,
        )
        final = living_domus_for_source(destination, width, kind="file", nonce=salt)
    except (OSError, UnicodeError, json.JSONDecodeError, TypeError, ValueError,
            RuntimeError, TardiSHAError):
        return False
    return stored == expected and stored_self == final
