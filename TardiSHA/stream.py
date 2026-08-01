"""Chunk-safe Accordion Manifold writer and local 110/144 packet governor."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, TextIO

from .canon import SATURATION_LIMIT, TOTAL_CAPACITY, court_node, court_active_connections, law, GLYPH_BODY
from .hashing import ALPHABET, TardiSHAError, validate_glyph, validate_middle_length
from .manifestation import ennead_saturate, manifestation_fold, vector_row
from .alqc_digest import alqc_hexdigest
from .tripartite import SHADOW_LOCUS_GLYPH

PACKET_WIDTH = TOTAL_CAPACITY
PACKET_DOMAIN = b"TARDISHA:LOCAL-COURT-PACKET\x00"


@dataclass(frozen=True, slots=True)
class LiquidHorizon:
    """Canon 110/144 Liquid horizon witness (plan §10.1, §11.12).

    The current Court-node i_h is the ACTUAL node supplied by the traversal — the
    singly-rooted Domus Court — never derived from the horizon number alone. Its
    active set is A_h = { j : (i_h + j) mod 144 < 110 } by the Deterministic Path
    Equation L_sat (Canon L730-738); W_h is the complement, the local Sacred No, and
    is always exactly 34. Not SuperNegative.
    """
    horizon: int
    current_court_index: int      # i_h, the actual current Court-node from traversal
    active_count: int             # always 110
    withheld_count: int           # always 34
    active: frozenset[int]        # A_h
    withheld: frozenset[int]      # W_h


def liquid_horizon(current_court_index: int, h: int) -> LiquidHorizon:
    """Horizon witness for the ACTUAL current Court-node (plan §11.12).

    current_court_index is the node the traversal is at (e.g. the root Domus
    Court). It is NOT recomputed as (root + h): the horizon number never stands in
    for the traversal's real node.
    """
    if isinstance(current_court_index, bool) or not isinstance(current_court_index, int) or not 0 <= current_court_index < TOTAL_CAPACITY:
        raise TardiSHAError("current Court index must be an exact integer in 0..143")
    if isinstance(h, bool) or not isinstance(h, int) or h < 0:
        raise TardiSHAError("horizon h must be a non-negative integer")
    i_h = current_court_index
    active = court_active_connections(i_h)            # L_sat active set, exactly 110
    withheld = frozenset(range(TOTAL_CAPACITY)) - active
    if len(active) != SATURATION_LIMIT or len(withheld) != TOTAL_CAPACITY - SATURATION_LIMIT:
        raise TardiSHAError("Canon horizon must be 110 active / 34 withheld (L720)")
    return LiquidHorizon(h, i_h, len(active), len(withheld), active, withheld)


@dataclass(frozen=True, slots=True)
class PacketAudit:
    packet_index: int
    characters: int
    current_court_index: int     # i_h from the Canon horizon (L_sat), not a hash scalar
    active_connections: int      # 110 by the governor
    withheld_connections: int    # 34 (local Sacred No)
    liquid_connection_image: float
    packet_proof: str
    resolution: str
    ennead_saturated: bool


@dataclass(frozen=True, slots=True)
class StreamReport:
    middle_length: int
    output_codepoints: int
    packet_width: int
    packet_count: int
    flow_packets: int
    quarantined_packets: int
    quarantine_samples: tuple[int, ...]

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def audit_packet(packet: str, packet_index: int, seed: bytes, root_court_index: int) -> PacketAudit:
    """Bind one written Synodic packet to its exact source-rooted Court horizon."""
    if type(packet) is not str or not packet or len(packet) > PACKET_WIDTH:
        raise TardiSHAError(f"packet must contain between 1 and {PACKET_WIDTH} characters")
    if any(character not in ALPHABET for character in packet):
        raise TardiSHAError("packet contains a non-Synodic Magicae glyph")
    if isinstance(packet_index, bool) or not isinstance(packet_index, int) or packet_index < 0:
        raise TardiSHAError("packet_index must be a non-negative integer")
    if type(seed) is not bytes or len(seed) != 32:
        raise TardiSHAError("packet seed must be the exact 32-byte coordinate root")
    hor = liquid_horizon(root_court_index, packet_index)
    governing_glyph = GLYPH_BODY[hor.current_court_index // 12]
    q2_pressure = abs(law(governing_glyph).q_vector[2])
    row = vector_row(manifestation_fold(hor.current_court_index))
    ennead_saturated = ennead_saturate(row, q2_pressure).saturated
    proof_body = (
        seed
        + root_court_index.to_bytes(2, "big")
        + packet_index.to_bytes(max(1, (packet_index.bit_length() + 7) // 8), "big")
        + b"\x00"
        + packet.encode("utf-8")
    )
    packet_proof = alqc_hexdigest(proof_body, domain=PACKET_DOMAIN)
    return PacketAudit(
        packet_index=packet_index,
        characters=len(packet),
        current_court_index=hor.current_court_index,
        active_connections=hor.active_count,
        withheld_connections=hor.withheld_count,
        liquid_connection_image=hor.active_count / TOTAL_CAPACITY,
        packet_proof=packet_proof,
        resolution="FLOW",
        ennead_saturated=ennead_saturated,
    )


def write_accordion_stream(
    handle: TextIO,
    *,
    origin_glyph: str,
    resolution_glyph: str,
    middle_chunks: Iterable[str],
    middle_length: int,
    seed: bytes,
    packet_manifest: TextIO | None = None,
) -> StreamReport:
    """Write glyph + dynamic middle + glyph with bounded memory and packet-local audit."""
    width = validate_middle_length(middle_length)
    origin = validate_glyph(origin_glyph, "origin_glyph")
    resolution = validate_glyph(resolution_glyph, "resolution_glyph")
    if type(seed) is not bytes or len(seed) != 32:
        raise TardiSHAError("stream seed must be the exact 32-byte coordinate root")
    handle.write(origin)
    if width == 0:
        for _chunk in middle_chunks:
            raise TardiSHAError("zero middle must not emit Synodic Magicae chunks")
        handle.write(SHADOW_LOCUS_GLYPH)
        handle.write(resolution)
        report = StreamReport(
            middle_length=0,
            output_codepoints=3,
            packet_width=PACKET_WIDTH,
            packet_count=0,
            flow_packets=0,
            quarantined_packets=0,
            quarantine_samples=(),
        )
        if packet_manifest is not None:
            packet_manifest.write(json.dumps({"type": "summary", **report.as_dict()}, separators=(",", ":")) + "\n")
        return report

    root_court_index = court_node(origin, resolution)  # k0 for the Liquid horizon

    pending = ""
    produced = 0
    packet_index = 0
    flow_packets = 0
    quarantined_packets = 0
    quarantine_samples: list[int] = []

    def commit_packet(packet: str) -> None:
        nonlocal packet_index, flow_packets, quarantined_packets
        audit = audit_packet(packet, packet_index, seed, root_court_index)
        handle.write(packet)
        if audit.resolution == "FLOW":
            flow_packets += 1
        else:
            quarantined_packets += 1
            quarantine_samples.append(packet_index)
        if packet_manifest is not None:
            packet_manifest.write(json.dumps({"type": "packet", **asdict(audit)}, separators=(",", ":")) + "\n")
        packet_index += 1

    for chunk in middle_chunks:
        if not isinstance(chunk, str) or any(character not in ALPHABET for character in chunk):
            raise TardiSHAError("middle stream emitted a non-Synodic Magicae chunk")
        if not chunk:
            raise TardiSHAError("middle stream emitted an empty chunk")
        produced += len(chunk)
        if produced > width:
            raise TardiSHAError("middle stream exceeded requested length")
        pending += chunk
        while len(pending) >= PACKET_WIDTH:
            commit_packet(pending[:PACKET_WIDTH])
            pending = pending[PACKET_WIDTH:]

    if produced != width:
        raise TardiSHAError(f"middle stream produced {produced} characters; expected {width}")
    if pending:
        commit_packet(pending)

    handle.write(resolution)
    report = StreamReport(
        middle_length=width,
        output_codepoints=width + 2,
        packet_width=PACKET_WIDTH,
        packet_count=packet_index,
        flow_packets=flow_packets,
        quarantined_packets=quarantined_packets,
        quarantine_samples=tuple(quarantine_samples),
    )
    if packet_manifest is not None:
        packet_manifest.write(json.dumps({"type": "summary", **report.as_dict()}, separators=(",", ":")) + "\n")
    return report


def count_codepoints(path: str | Path, *, chunk_characters: int = 1024 * 1024) -> int:
    total = 0
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        while True:
            chunk = handle.read(chunk_characters)
            if not chunk:
                break
            total += len(chunk)
    return total
