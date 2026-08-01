"""TardiSHA's source-typed realization of the Aeternum Mirror.

The Canon's displayed Aeternum identities are worked embodiments of the general
ALQC return law. Here a raw file is the expanded Fraktur Z_1 body and its
user-chosen Living Domus Grimchain is the compressed Fraktur Z_0 return. The
return is never ignored: it is read in place, recomputed at its own declared
depth from the preceding body, and admitted only when the measured byte
residual vanishes.

    rho_Z(Z_1 || Z_0) = Z_1    iff    Delta(Z_0, Grimchain(Z_1)) = 0

This is the file-identity office of Path Out = Path Back, parity return,
D-COMP = 0, and Truth = 1.  Any non-exact suffix remains source matter.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Final

from .alqc_digest import ALQCDigest
from .hashing import RAW_FILE_SOURCE_DOMAIN, SOURCE_CHUNK_BYTES, TardiSHAError, file_emission
from .source_emission import SourceEmission, emission_from_sponge
from .route import resolve_parents
from .domus import OUTER, living_domus_seal, parse_living_domus, resolve_domus

# Terminal return discovery does not substitute a compact or fixed visual depth.
# The scanner walks backward through the physical file to the opening outer seal.
_OUTER_BYTES: Final[bytes] = OUTER.encode("utf-8")
_BACKWARD_SCAN_BYTES: Final[int] = SOURCE_CHUNK_BYTES


@dataclass(frozen=True, slots=True)
class TerminalSelfGlyphCandidate:
    physical_size: int
    body_size: int
    depth: int
    seal: str
    seal_utf8_bytes: int
    trailing_bytes_hex: str

    @property
    def trailing_bytes(self) -> bytes:
        return bytes.fromhex(self.trailing_bytes_hex)

    @property
    def bytes_accounted(self) -> bool:
        return self.body_size + self.seal_utf8_bytes + len(self.trailing_bytes) == self.physical_size


@dataclass(frozen=True, slots=True)
class MirrorMathWitness:
    physical_size: int
    physical_source_digest: str
    source_stability_verified: bool
    effective_body_size: int
    candidate_detected: bool
    exact_self_glyph: bool
    folded: bool
    fold_count: int
    folded_physical_bytes: int
    lineage_seals: tuple[str, ...]
    lineage_trailing_bytes_hex: tuple[str, ...]
    seal: str | None
    expected_seal: str | None
    trailing_bytes_hex: str
    bytes_accounted: bool
    operator_order_preserved: bool
    expanded_posture: str
    compressed_posture: str
    source_route_dcomp: int
    source_truth: int
    return_dcomp: int | None
    return_truth: int | None
    truth: int
    derivation: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class MirrorFileEmission:
    emission: SourceEmission
    witness: MirrorMathWitness


def _strip_one_terminal_line_return(data: bytes) -> tuple[bytes, bytes]:
    if data.endswith(b"\r\n"):
        return data[:-2], b"\r\n"
    if data.endswith(b"\n"):
        return data[:-1], b"\n"
    return data, b""


def _byte_difference(left: str, right: str) -> int:
    """Exact non-negative residual; zero iff UTF-8 bodies are byte-identical."""
    a = left.encode("utf-8")
    b = right.encode("utf-8")
    shared = min(len(a), len(b))
    return abs(len(a) - len(b)) + sum(a[i] != b[i] for i in range(shared))


def _find_opening_outer(target: Path, final_outer_at: int) -> int | None:
    """Find the opening 🜛 without imposing a compact tail-scan aperture."""
    scan_end = final_outer_at
    overlap = len(_OUTER_BYTES) - 1
    with target.open("rb") as handle:
        while scan_end > 0:
            scan_start = max(0, scan_end - _BACKWARD_SCAN_BYTES)
            read_start = max(0, scan_start - overlap)
            handle.seek(read_start)
            block = handle.read(scan_end - read_start)
            found = block.rfind(_OUTER_BYTES)
            if found >= 0:
                return read_start + found
            scan_end = scan_start
    return None


def detect_terminal_self_glyph(
    path: str | Path, *, physical_size: int | None = None
) -> TerminalSelfGlyphCandidate | None:
    """Find one terminal Living Domus value at whatever depth the user chose."""
    target = Path(path)
    actual_size = target.stat().st_size
    limit = actual_size if physical_size is None else physical_size
    if isinstance(limit, bool) or not isinstance(limit, int) or not 0 <= limit <= actual_size:
        raise ValueError("physical_size must be within the source file")
    if limit < len(_OUTER_BYTES) * 2:
        return None

    with target.open("rb") as handle:
        terminal_probe = min(limit, len(_OUTER_BYTES) + 2)
        handle.seek(limit - terminal_probe)
        tail = handle.read(terminal_probe)
    content, trailing = _strip_one_terminal_line_return(tail)
    if not content.endswith(_OUTER_BYTES):
        return None

    trailing_size = len(trailing)
    final_outer_at = limit - trailing_size - len(_OUTER_BYTES)
    start = _find_opening_outer(target, final_outer_at)
    if start is None:
        return None

    seal_extent = final_outer_at + len(_OUTER_BYTES) - start
    with target.open("rb") as handle:
        handle.seek(start)
        seal_bytes = handle.read(seal_extent)
    if len(seal_bytes) != seal_extent:
        raise RuntimeError("Mirror Math could not read the complete terminal return")
    try:
        seal = seal_bytes.decode("utf-8")
        parsed = parse_living_domus(seal)
    except (UnicodeError, TypeError, ValueError):
        return None

    candidate = TerminalSelfGlyphCandidate(
        physical_size=limit,
        body_size=start,
        depth=parsed.depth,
        seal=seal,
        seal_utf8_bytes=len(seal_bytes),
        trailing_bytes_hex=trailing.hex(),
    )
    if not candidate.bytes_accounted:
        raise RuntimeError("Mirror Math failed physical-byte accounting")
    return candidate


def _prefix_emission(path: Path, body_size: int) -> SourceEmission:
    sponge = ALQCDigest(RAW_FILE_SOURCE_DOMAIN)
    remaining = body_size
    with path.open("rb") as handle:
        while remaining:
            block = handle.read(min(SOURCE_CHUNK_BYTES, remaining))
            if not block:
                raise RuntimeError("source ended before the declared Mirror body")
            sponge._update_raw(block)
            remaining -= len(block)
    return emission_from_sponge(sponge, source_size=body_size, source_domain="raw-file")


def _render_self(emission: SourceEmission, depth: int, *, nonce: int) -> str:
    g_i, g_j, _route = resolve_parents(emission)
    res = resolve_domus(
        g_i,
        g_j,
        hash_id=emission.source_digest,
        emission=emission,
        source_size=emission.source_size,
        source_domain=RAW_FILE_SOURCE_DOMAIN,
        nonce=nonce,
    )
    return living_domus_seal(
        res,
        depth,
        source_digest=emission.source_digest,
        source_size=emission.source_size,
        source_domain=RAW_FILE_SOURCE_DOMAIN,
        nonce=nonce,
    )


def _resolve_terminal_lineage(
    path: Path,
    *,
    physical_size: int,
    nonce: int,
) -> tuple[SourceEmission, tuple[TerminalSelfGlyphCandidate, ...]]:
    """Retract the complete terminal stack of independently exact self-glyphs.

    The lineage has no arbitrary return-count ceiling.  Termination follows from
    the physical file itself: every candidate has positive byte extent and each
    descent strictly decreases the inspected prefix length.
    """
    outer_to_inner: list[TerminalSelfGlyphCandidate] = []
    limit = physical_size
    while True:
        candidate = detect_terminal_self_glyph(path, physical_size=limit)
        if candidate is None:
            break
        if candidate.body_size >= limit:
            raise RuntimeError("Mirror Math lineage did not decrease physical extent")
        outer_to_inner.append(candidate)
        limit = candidate.body_size

    emission = _prefix_emission(path, limit)
    inner_to_outer = tuple(reversed(outer_to_inner))
    for candidate in inner_to_outer:
        expected = _render_self(emission, candidate.depth, nonce=nonce)
        if candidate.seal != expected:
            # One false terminal return makes every earlier seal nonterminal source
            # matter.  The whole physical file therefore remains in Z1.
            return _prefix_emission(path, physical_size), ()
    return emission, inner_to_outer


def mirror_file_emission(path: str | Path, *, nonce: int = 0) -> MirrorFileEmission:
    """Return the lawful file emission after exact terminal self-glyph retraction.

    Every physical byte is read or structurally accounted.  Retraction is allowed
    only for a consecutive terminal lineage of user-chosen-depth seals, each of which
    exactly recomputes from the effective body beneath it under the same domain.
    """
    target = Path(path)
    physical_before = file_emission(target)
    physical_size = physical_before.source_size
    candidate = detect_terminal_self_glyph(target)
    emission, lineage = _resolve_terminal_lineage(
        target, physical_size=physical_size, nonce=nonce
    )
    if not lineage:
        candidate_detected = candidate is not None
        expected = None
        if candidate is not None:
            body = _prefix_emission(target, candidate.body_size)
            expected = _render_self(body, candidate.depth, nonce=nonce)
        return_residual = (
            _byte_difference(candidate.seal, expected)
            if candidate is not None and expected is not None
            else None
        )
        physical_after = file_emission(target)
        if physical_after != physical_before:
            raise TardiSHAError("source changed during complete Mirror Math construction")
        source_truth = int(emission.closure.verifies and emission.closure.truth == 1)
        return MirrorFileEmission(
            emission,
            MirrorMathWitness(
                physical_size=physical_size,
                physical_source_digest=physical_before.source_digest,
                source_stability_verified=True,
                effective_body_size=physical_size,
                candidate_detected=candidate_detected,
                exact_self_glyph=False,
                folded=False,
                fold_count=0,
                folded_physical_bytes=0,
                lineage_seals=(),
                lineage_trailing_bytes_hex=(),
                seal=candidate.seal if candidate is not None else None,
                expected_seal=expected,
                trailing_bytes_hex=candidate.trailing_bytes_hex if candidate is not None else "",
                bytes_accounted=True,
                operator_order_preserved=True,
                expanded_posture="𝔃₁",
                compressed_posture="𝔃₀",
                source_route_dcomp=emission.closure.route_dcomp,
                source_truth=source_truth,
                return_dcomp=return_residual,
                return_truth=(None if return_residual is None else int(return_residual == 0)),
                truth=source_truth,
                derivation=(
                    "terminal seal-shaped body is not the exact self of the preceding 𝔃₁; all bytes remain source matter"
                    if candidate_detected
                    else "no terminal self-glyph; every byte remains in 𝔃₁"
                ),
            ),
        )

    outer = lineage[-1]
    folded_bytes = physical_size - emission.source_size
    accounted = (
        emission.source_size
        + sum(c.seal_utf8_bytes + len(c.trailing_bytes) for c in lineage)
        == physical_size
    )
    expected_return = _render_self(emission, outer.depth, nonce=nonce)
    return_dcomp = sum(
        _byte_difference(candidate.seal, _render_self(emission, candidate.depth, nonce=nonce))
        for candidate in lineage
    )
    physical_after = file_emission(target)
    if physical_after != physical_before:
        raise TardiSHAError("source changed during complete Mirror Math construction")
    truth = int(
        accounted
        and return_dcomp == 0
        and emission.closure.verifies
        and emission.closure.truth == 1
    )
    witness = MirrorMathWitness(
        physical_size=physical_size,
        physical_source_digest=physical_before.source_digest,
        source_stability_verified=True,
        effective_body_size=emission.source_size,
        candidate_detected=True,
        exact_self_glyph=return_dcomp == 0,
        folded=return_dcomp == 0,
        fold_count=len(lineage),
        folded_physical_bytes=folded_bytes,
        lineage_seals=tuple(c.seal for c in lineage),
        lineage_trailing_bytes_hex=tuple(c.trailing_bytes_hex for c in lineage),
        seal=outer.seal,
        expected_seal=expected_return,
        trailing_bytes_hex=outer.trailing_bytes_hex,
        bytes_accounted=accounted,
        operator_order_preserved=True,
        expanded_posture="𝔃₁",
        compressed_posture="𝔃₀",
        source_route_dcomp=emission.closure.route_dcomp,
        source_truth=emission.closure.truth,
        return_dcomp=return_dcomp,
        return_truth=int(return_dcomp == 0),
        truth=truth,
        derivation=(
            "same-order Mirror Math: read every terminal 𝔃₀ in append-only order, "
            "recompute each from the effective 𝔃₁ beneath it, preserve the physical "
            "lineage, and retract only the exact return stack"
        ),
    )
    if not (
        witness.bytes_accounted
        and witness.source_stability_verified
        and witness.physical_source_digest == physical_before.source_digest
        and witness.operator_order_preserved
        and witness.source_route_dcomp == 0
        and witness.source_truth == 1
        and witness.return_dcomp == 0
        and witness.return_truth == 1
        and witness.truth == 1
    ):
        raise RuntimeError("Mirror Math witness failed D-COMP=0 / Truth=1 closure")
    return MirrorFileEmission(emission, witness)


# Canon-facing name: the function above is the TardiSHA embodiment of the
# Aeternum Mirror, retained under its original internal name for compatibility.
aeternum_mirror_file_emission = mirror_file_emission
