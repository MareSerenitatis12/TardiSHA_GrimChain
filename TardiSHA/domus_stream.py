"""Bounded-memory streaming for the visible Court-rooted Domus Aeon.

The center is the Shadow Locus `⛎` at depth zero and the
prefix-stable Synodic Magicae body at positive depth.  Its seed is derived through the
governing Court C and alternating Court D, Infinite Yes, and Sacred No.  No Goetic boundary
is reused as a Domus stream coordinate.
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Literal

from .hashing import (
    TardiSHAError,
    file_emission,
    directory_emission,
    iter_middle,
    validate_nonce,
    validate_middle_length,
    RAW_FILE_SOURCE_DOMAIN,
    DIRECTORY_SOURCE_DOMAIN,
)
from .route import SourceRouteWitness, resolve_parents
from .source_emission import SourceEmission
from .mirror_math import mirror_file_emission
from .stream import count_codepoints
from .regia import iter_regia_middle, regia_middle
from .domus import (
    resolve_domus,
    domus_center_seed,
    seal_head,
    seal_tail,
    living_domus_seal,
    ZERO_MIDDLE_GLYPH,
)

Kind = Literal["file", "directory"]

# Fixed non-center code-point count: head (15) + tail (15). Total seal length is
# _FIXED + center_length, where center_length == 1 at depth 0 (⛎) and == n>0.
_FIXED = 30


_DOMAIN_LABEL = {"file": "raw-file", "directory": "directory"}


def _validate_kind(kind: Kind) -> Kind:
    if kind not in ("file", "directory"):
        raise TardiSHAError("kind must be exactly 'file' or 'directory'")
    return kind


def _fingerprint(source: Path, kind: Kind, *, nonce: int = 0) -> tuple[SourceEmission, bytes]:
    source_kind = _validate_kind(kind)
    if source_kind == "file":
        return mirror_file_emission(source, nonce=nonce).emission, RAW_FILE_SOURCE_DOMAIN
    emission, _entries = directory_emission(source)
    return emission, DIRECTORY_SOURCE_DOMAIN


def _resolve_pair(
    emission: SourceEmission, witness: SourceRouteWitness | None = None
) -> tuple[str, str, SourceRouteWitness]:
    return resolve_parents(emission, witness=witness)


def living_domus_from_emission(
    emission: SourceEmission,
    middle: int,
    *,
    nonce: int = 0,
    route_witness: SourceRouteWitness | None = None,
) -> str:
    """Render a file seal from an already witnessed Q1 emission.

    This is the cache/parallel join point.  It performs no source-content read.
    """
    salt = validate_nonce(nonce)
    width = validate_middle_length(middle)
    if emission.source_domain != "raw-file":
        raise ValueError("living_domus_from_emission requires a raw-file emission")
    g_i, g_j, witness = _resolve_pair(emission, route_witness)
    digest, size = emission.source_digest, emission.source_size
    res = resolve_domus(
        g_i,
        g_j,
        hash_id=digest,
        emission=emission,
        source_size=size,
        source_domain=RAW_FILE_SOURCE_DOMAIN,
        nonce=salt,
    )
    return living_domus_seal(
        res, width, source_digest=digest, source_size=size, nonce=salt,
        source_domain=RAW_FILE_SOURCE_DOMAIN,
    )


def file_domus_record(
    source: str | Path, middle: int, *, nonce: int = 0
) -> tuple[str, SourceEmission, SourceRouteWitness]:
    """Read one file, return its seal plus complete cacheable witnesses."""
    salt = validate_nonce(nonce)
    emission = mirror_file_emission(Path(source), nonce=salt).emission
    g_i, g_j, witness = _resolve_pair(emission)
    seal = living_domus_from_emission(
        emission, middle, nonce=salt, route_witness=witness
    )
    return seal, emission, witness


def living_domus_for_source(source: Path, middle: int, *, kind: Kind, nonce: int = 0) -> str:
    """In-memory Living Domus seal for a file or directory (bounded to small middle)."""
    salt = validate_nonce(nonce)
    source_kind = _validate_kind(kind)
    if source_kind == "file":
        seal, _emission, _witness = file_domus_record(source, middle, nonce=salt)
        return seal
    emission, domain = _fingerprint(source, source_kind, nonce=salt)
    digest, size = emission.source_digest, emission.source_size
    g_i, g_j, _witness = _resolve_pair(emission)
    res = resolve_domus(
        g_i,
        g_j,
        hash_id=digest,
        emission=emission,
        source_size=size,
        source_domain=domain,
        nonce=salt,
    )
    return living_domus_seal(
        res, middle, source_digest=digest, source_size=size, nonce=salt, source_domain=domain
    )


def write_living_domus_seal(
    source_path: str | Path,
    output_path: str | Path,
    *,
    kind: Kind,
    middle_length: int,
    nonce: int = 0,
) -> dict:
    """Stream a Living Domus seal to disk with bounded memory and atomic commit.

    Writes: seal_head, then the center (⛎ at depth 0, else the native
    Synodic Magicae stream), then seal_tail. Re-fingerprints afterward to refuse a source
    that changed mid-write, mirroring the existing streaming writers.
    """
    width = validate_middle_length(middle_length)
    salt = validate_nonce(nonce)
    source_kind = _validate_kind(kind)
    source = Path(source_path)
    output = Path(output_path)
    if source.resolve() == output.resolve():
        raise TardiSHAError("source_path and output_path must be different paths")

    emission, domain = _fingerprint(source, source_kind, nonce=salt)
    digest, size = emission.source_digest, emission.source_size
    g_i, g_j, _witness = _resolve_pair(emission)
    res = resolve_domus(
        g_i,
        g_j,
        hash_id=digest,
        emission=emission,
        source_size=size,
        source_domain=domain,
        nonce=salt,
    )
    head, tail = seal_head(res), seal_tail(res)

    output.parent.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", newline="", delete=False,
        dir=output.parent, prefix=f".{output.name}.", suffix=".part",
    )
    temp = Path(handle.name)
    center_len = 1 if width == 0 else width
    try:
        with handle:
            handle.write(head)
            if width == 0:
                handle.write(ZERO_MIDDLE_GLYPH)
            else:
                seed = domus_center_seed(res, source_domain=domain, nonce=salt)
                for chunk in iter_regia_middle(seed, width):
                    handle.write(chunk)
            handle.write(tail)
            handle.flush()
            os.fsync(handle.fileno())
    except Exception:
        temp.unlink(missing_ok=True)
        raise

    # Refuse a source that changed while the (possibly enormous) seal was written.
    after, after_domain = _fingerprint(source, source_kind, nonce=salt)
    if after != emission or after_domain != domain:
        temp.unlink(missing_ok=True)
        raise TardiSHAError("source changed while the Living Domus seal was being written")

    os.replace(temp, output)
    return {
        "output": str(output),
        "governing_goetic": g_i,
        "hyperbolic_parent": g_j,
        "root_court_glyph": res.root_court.glyph,
        "alternating_court_glyph": res.alternating_court.glyph,
        "middle_length": width,
        "sealed_length": _FIXED + center_len,
        "source_digest": digest,
        "source_size": size,
    }


def verify_living_domus_value(
    seal: str,
    source_path: str | Path,
    *,
    kind: Kind,
    nonce: int = 0,
) -> bool:
    """Verify an inline Living Domus seal string against a file/dir source.

    Fingerprints the source, derives (g_i, g_j) from the boundary route, parses
    the seal's depth, recomputes the whole seal, and compares. Used by the
    checksum-list (`-c`) path where the seal is a value, not a file.
    """
    from .domus import parse_living_domus
    try:
        source_kind = _validate_kind(kind)
        parsed = parse_living_domus(seal)
        recomputed = living_domus_for_source(Path(source_path), parsed.depth, kind=source_kind, nonce=nonce)
        return recomputed == seal
    except (OSError, TypeError, ValueError, TardiSHAError, UnicodeError):
        return False


def verify_living_domus_seal(
    seal_path: str | Path,
    source_path: str | Path,
    *,
    kind: Kind,
    nonce: int = 0,
) -> bool:
    """Verify a possibly enormous Living Domus seal file without loading it whole.

    Recomputes head/tail and the center from the source and compares streaming,
    code point by code point. Shape is never trusted: the Court glyphs, Q
    witnesses, and every center code point are recomputed from the source digest through its ordered Courts.
    """
    try:
        seal_file = Path(seal_path)
        total = count_codepoints(seal_file)
        if total < _FIXED + 1:
            return False
        center_len = total - _FIXED
        salt = validate_nonce(nonce)
        source_kind = _validate_kind(kind)
        source = Path(source_path)
        emission, domain = _fingerprint(source, source_kind, nonce=salt)
        digest, size = emission.source_digest, emission.source_size
        g_i, g_j, _witness = _resolve_pair(emission)
        res = resolve_domus(
            g_i,
            g_j,
            hash_id=digest,
            emission=emission,
            source_size=size,
            source_domain=domain,
            nonce=salt,
        )
        head, tail = seal_head(res), seal_tail(res)

        with seal_file.open("r", encoding="utf-8", newline="") as h:
            if h.read(len(head)) != head:
                return False
            if center_len == 1:
                first = h.read(1)
                if first == ZERO_MIDDLE_GLYPH:
                    pass  # depth 0: Shadow Locus center fully determined by head/tail
                else:
                    seed = domus_center_seed(res, source_domain=domain, nonce=salt)
                    expected = regia_middle(seed, 1)
                    if first != expected:
                        return False
            else:
                seed = domus_center_seed(res, source_domain=domain, nonce=salt)
                for chunk in iter_regia_middle(seed, center_len):
                    expected_chunk = chunk
                    if h.read(len(expected_chunk)) != expected_chunk:
                        return False
            if h.read(len(tail)) != tail:
                return False
            if h.read(1) != "":
                return False
        after, after_domain = _fingerprint(source, source_kind, nonce=salt)
        return after == emission and after_domain == domain
    except (OSError, TypeError, ValueError, TardiSHAError, UnicodeError):
        return False
