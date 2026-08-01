"""Reversible content-addressed TardiSHA archive mode."""
from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from .alqc_digest import ALQCDigest, alqc_hexdigest
from .hashing import RAW_FILE_SOURCE_DOMAIN, SOURCE_CHUNK_BYTES, TardiSHAError, file_emission
from .node import TardiSHANode, node_from_file
from .domus import resolve_domus, living_domus_seal
from .court_registry import full_name
from .route import (
    SourceRouteWitness,
    parents_t,
    source_route_witness_from_emission,
    verify_source,
)
from .source_emission import emission_from_sponge

ARCHIVE_ROOT_DOMAIN = b"TARDISHA:ARCHIVE-ROOT\x00"
ARCHIVE_CHUNK_DOMAIN = b"TARDISHA:ARCHIVE-CHUNK\x00"
_CHUNK_DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")


def _validate_chunk(chunk: "ArchiveChunk", *, expected_index: int | None = None) -> None:
    if isinstance(chunk.index, bool) or not isinstance(chunk.index, int) or chunk.index < 0:
        raise TardiSHAError("archive chunk index must be a non-negative integer")
    if expected_index is not None and chunk.index != expected_index:
        raise TardiSHAError("archive chunk indices must be contiguous and ordered")
    if isinstance(chunk.offset, bool) or not isinstance(chunk.offset, int) or chunk.offset < 0:
        raise TardiSHAError("archive chunk offset must be a non-negative integer")
    if isinstance(chunk.size, bool) or not isinstance(chunk.size, int) or chunk.size < 1:
        raise TardiSHAError("archive chunk size must be a positive integer")
    if not isinstance(chunk.digest, str) or not _CHUNK_DIGEST_RE.fullmatch(chunk.digest):
        raise TardiSHAError("archive chunk digest must be 64 lowercase hexadecimal characters")


@dataclass(frozen=True, slots=True)
class ArchiveChunk:
    index: int
    offset: int
    size: int
    digest: str


@dataclass(frozen=True, slots=True)
class TardiSHAArchiveManifest:
    archive_root: str
    source_digest: str
    source_size: int
    chunk_size: int
    chunks: tuple[ArchiveChunk, ...]
    node: TardiSHANode

    def __post_init__(self) -> None:
        if self.node.mode != "ARCHIVE_REVERSIBLE":
            raise TardiSHAError("archive manifest requires an ARCHIVE_REVERSIBLE node")
        if self.node.archive_root != self.archive_root:
            raise TardiSHAError("archive manifest root must equal the node archive_root")
        if self.node.source_domain != "raw-file":
            raise TardiSHAError("archive manifest requires a raw-file source proof")
        if self.node.route_witness is None or not verify_source(
            self.node.route_witness.emission, self.node.route_witness
        ):
            raise TardiSHAError("archive manifest requires exact return-bearing source proof")

    def as_dict(self) -> dict[str, object]:
        return {
            "archive_root": self.archive_root,
            "source_digest": self.source_digest,
            "source_size": self.source_size,
            "chunk_size": self.chunk_size,
            "chunks": [asdict(chunk) for chunk in self.chunks],
            "node": self.node.as_dict(),
            # Additive Living Domus witness (plan §11.16). Derived from the node's
            # already-committed ordered Goetics + source digest; NOT part of the
            # archive_root digest and NOT used by restore — a recorded witness only.
            "living_domus": _living_domus_block(self.node),
        }


def _living_domus_block(node: TardiSHANode) -> dict[str, object]:
    """Record the zero-middle return witness in its exact JSON representation."""
    body = node.domus_witness(middle_length=0)
    return json.loads(json.dumps(body, ensure_ascii=False, sort_keys=True))


def _node_root_body(
    *,
    source_digest: str,
    source_size: int,
    origin_glyph: str,
    resolution_glyph: str,
    nonce: int,
    source_domain: str,
    route_witness: SourceRouteWitness,
) -> dict[str, object]:
    if source_domain != "raw-file":
        raise TardiSHAError("archive root body requires the raw-file source domain")
    if not verify_source(route_witness.emission, route_witness):
        raise TardiSHAError("archive root body requires exact return-bearing source proof")
    return {
        "source_digest": source_digest,
        "source_size": source_size,
        "origin_glyph": origin_glyph,
        "resolution_glyph": resolution_glyph,
        "nonce": nonce,
        "source_domain": source_domain,
        "route_witness": route_witness.as_dict(),
    }


def _node_root_body_from_node(node: TardiSHANode) -> dict[str, object]:
    if node.route_witness is None:
        raise TardiSHAError("archive node requires a complete Final Equation Z route witness")
    return _node_root_body(
        source_digest=node.source_digest,
        source_size=node.source_size,
        origin_glyph=node.origin_glyph,
        resolution_glyph=node.resolution_glyph,
        nonce=node.nonce,
        source_domain=node.source_domain,
        route_witness=node.route_witness,
    )


def _root_payload(
    source_digest: str,
    source_size: int,
    chunk_size: int,
    chunks: tuple[ArchiveChunk, ...],
    node_root_body: dict[str, object],
) -> bytes:
    return json.dumps(
        {
            "source_digest": source_digest,
            "source_size": source_size,
            "chunk_size": chunk_size,
            "chunks": [asdict(chunk) for chunk in chunks],
            "node": node_root_body,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _archive_root(
    source_digest: str,
    source_size: int,
    chunk_size: int,
    chunks: tuple[ArchiveChunk, ...],
    node_root_body: dict[str, object],
) -> str:
    return alqc_hexdigest(
        _root_payload(source_digest, source_size, chunk_size, chunks, node_root_body),
        domain=ARCHIVE_ROOT_DOMAIN,
    )


def _chunk_digest(data: bytes) -> str:
    return alqc_hexdigest(data, domain=ARCHIVE_CHUNK_DOMAIN)


def create_archive(
    source_path: str | Path,
    archive_dir: str | Path,
    *,
    chunk_size: int = SOURCE_CHUNK_BYTES,
) -> TardiSHAArchiveManifest:
    if isinstance(chunk_size, bool) or not isinstance(chunk_size, int) or chunk_size < 1:
        raise TardiSHAError("chunk_size must be a positive integer")
    source = Path(source_path)
    target = Path(archive_dir)
    chunks_dir = target / "chunks"
    chunks_dir.mkdir(parents=True, exist_ok=True)

    chunks: list[ArchiveChunk] = []
    offset = 0
    index = 0
    digest = ALQCDigest(RAW_FILE_SOURCE_DOMAIN)
    with source.open("rb") as handle:
        while True:
            data = handle.read(chunk_size)
            if not data:
                break
            digest._update_raw(data)
            chunk_digest = _chunk_digest(data)
            chunk_path = chunks_dir / f"{chunk_digest}.bin"
            if chunk_path.exists():
                existing = chunk_path.read_bytes()
                if existing != data or _chunk_digest(existing) != chunk_digest:
                    raise TardiSHAError(
                        f"archive chunk {chunk_digest} already exists but its content is not true"
                    )
            else:
                tmp = chunk_path.with_suffix(".bin.part")
                tmp.write_bytes(data)
                os.replace(tmp, chunk_path)
            chunks.append(ArchiveChunk(index=index, offset=offset, size=len(data), digest=chunk_digest))
            offset += len(data)
            index += 1

    source_size = offset
    source_emission = emission_from_sponge(
        digest,
        source_size=source_size,
        source_domain="raw-file",
    )
    confirmed_emission = file_emission(source)
    if confirmed_emission != source_emission:
        raise TardiSHAError("source changed during archive creation")
    source_emission = confirmed_emission
    source_digest = source_emission.source_digest
    chunk_tuple = tuple(chunks)
    route_witness = source_route_witness_from_emission(source_emission)
    origin_glyph, resolution_glyph = parents_t(route_witness)
    proof_body = _node_root_body(
        source_digest=source_digest,
        source_size=source_size,
        origin_glyph=origin_glyph,
        resolution_glyph=resolution_glyph,
        nonce=0,
        source_domain="raw-file",
        route_witness=route_witness,
    )
    _verify_source_from_chunks(chunks_dir, chunk_tuple, route_witness)
    root = _archive_root(source_digest, source_size, chunk_size, chunk_tuple, proof_body)
    node = node_from_file(
        source,
        mode="ARCHIVE_REVERSIBLE",
        nonce=0,
        mirror_self=False,
        archive_root=root,
    )
    if _node_root_body_from_node(node) != proof_body:
        raise TardiSHAError("source changed between archive-root proof and final archive node")
    manifest = TardiSHAArchiveManifest(root, source_digest, source_size, chunk_size, chunk_tuple, node)
    (target / "manifest.json").write_text(json.dumps(manifest.as_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def read_archive_manifest(manifest_path: str | Path) -> TardiSHAArchiveManifest:
    data = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TardiSHAError("archive manifest must be a JSON object")
    source_size = data.get("source_size")
    chunk_size = data.get("chunk_size")
    if isinstance(source_size, bool) or not isinstance(source_size, int) or source_size < 0:
        raise TardiSHAError("archive source_size must be a non-negative integer")
    if isinstance(chunk_size, bool) or not isinstance(chunk_size, int) or chunk_size < 1:
        raise TardiSHAError("archive chunk_size must be a positive integer")
    for field in ("archive_root", "source_digest"):
        value = data.get(field)
        if not isinstance(value, str) or not _CHUNK_DIGEST_RE.fullmatch(value):
            raise TardiSHAError(f"archive {field} must be 64 lowercase hexadecimal characters")
    raw_chunks = data.get("chunks")
    if not isinstance(raw_chunks, list):
        raise TardiSHAError("archive chunks must be a list")
    try:
        chunks = tuple(ArchiveChunk(**chunk) for chunk in raw_chunks)
    except (TypeError, KeyError) as exc:
        raise TardiSHAError("archive chunk body is malformed") from exc
    expected_count = 0 if source_size == 0 else (source_size + chunk_size - 1) // chunk_size
    if len(chunks) != expected_count:
        raise TardiSHAError("archive chunk count contradicts source_size and chunk_size")
    expected_offset = 0
    for expected_index, chunk in enumerate(chunks):
        _validate_chunk(chunk, expected_index=expected_index)
        if chunk.offset != expected_offset:
            raise TardiSHAError("archive chunk offsets must be contiguous")
        if chunk.size > chunk_size:
            raise TardiSHAError("archive chunk size exceeds declared chunk_size")
        if expected_index < len(chunks) - 1 and chunk.size != chunk_size:
            raise TardiSHAError("every non-terminal archive chunk must equal chunk_size")
        expected_offset += chunk.size
    if expected_offset != source_size:
        raise TardiSHAError("archive chunk sizes do not equal source_size")
    node_data = data.get("node")
    if not isinstance(node_data, dict):
        raise TardiSHAError("archive node must be an object")
    if data.get("source_digest") != node_data.get("source_digest"):
        raise TardiSHAError(
            "archive manifest source_digest mismatch between top-level "
            "and nested node: archive root recomputation must fail"
        )
    if data.get("source_size") != node_data.get("source_size"):
        raise TardiSHAError("archive manifest source_size mismatch between top-level and nested node")
    if node_data.get("mode") != "ARCHIVE_REVERSIBLE":
        raise TardiSHAError("archive node mode must be ARCHIVE_REVERSIBLE")
    if node_data.get("source_domain") != "raw-file":
        raise TardiSHAError("archive node source_domain mismatch")
    if "route_witness" not in node_data:
        raise TardiSHAError("archive node is missing its Final Equation Z route witness")
    route_witness = SourceRouteWitness.from_dict(node_data["route_witness"])
    node = TardiSHANode(
        mode=node_data["mode"],
        source_digest=node_data["source_digest"],
        source_size=node_data["source_size"],
        origin_glyph=node_data["origin_glyph"],
        resolution_glyph=node_data["resolution_glyph"],
        nonce=node_data["nonce"],
        source_domain=node_data["source_domain"],
        route_witness=route_witness,
        archive_root=node_data.get("archive_root"),
        finite_extent=node_data.get("finite_extent"),
    )
    if node_data.get("node_id") != node.node_id:
        raise TardiSHAError("archive node_id witness is forged or stale")
    supplied_domus = data.get("living_domus")
    if not isinstance(supplied_domus, dict) or supplied_domus != _living_domus_block(node):
        raise TardiSHAError("archive living_domus witness is forged or stale")
    root = _archive_root(
        data["source_digest"],
        data["source_size"],
        data["chunk_size"],
        chunks,
        _node_root_body_from_node(node),
    )
    if root != data["archive_root"] or node.archive_root != root:
        raise TardiSHAError("archive manifest root mismatch")
    return TardiSHAArchiveManifest(root, data["source_digest"], data["source_size"], data["chunk_size"], chunks, node)


def _verify_source_from_chunks(
    chunks_dir: Path,
    chunks: tuple[ArchiveChunk, ...],
    route_witness: SourceRouteWitness,
) -> None:
    digest = ALQCDigest(RAW_FILE_SOURCE_DOMAIN)
    size = 0
    for chunk in chunks:
        data = (chunks_dir / f"{chunk.digest}.bin").read_bytes()
        if len(data) != chunk.size or _chunk_digest(data) != chunk.digest:
            raise TardiSHAError(f"archive chunk {chunk.index} failed verification")
        digest._update_raw(data)
        size += len(data)
    emission = emission_from_sponge(digest, source_size=size, source_domain="raw-file")
    if not verify_source(emission, route_witness):
        raise TardiSHAError("archive chunk content does not reproduce the stored source route witness")


def restore_archive(
    manifest_path: str | Path,
    archive_dir: str | Path,
    output_path: str | Path,
) -> Path:
    manifest = read_archive_manifest(manifest_path)
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_name(f".{target.name}.part")
    digest = ALQCDigest(RAW_FILE_SOURCE_DOMAIN)
    chunks_dir = Path(archive_dir) / "chunks"
    with temp.open("wb") as out:
        for chunk in manifest.chunks:
            data = (chunks_dir / f"{chunk.digest}.bin").read_bytes()
            if len(data) != chunk.size or _chunk_digest(data) != chunk.digest:
                raise TardiSHAError(f"archive chunk {chunk.index} failed verification")
            digest._update_raw(data)
            out.write(data)
        out.flush()
        os.fsync(out.fileno())
    restored_emission = emission_from_sponge(
        digest,
        source_size=temp.stat().st_size,
        source_domain="raw-file",
    )
    if (
        restored_emission.source_digest != manifest.source_digest
        or restored_emission.source_size != manifest.source_size
        or manifest.node.route_witness is None
        or not verify_source(restored_emission, manifest.node.route_witness)
    ):
        temp.unlink(missing_ok=True)
        raise TardiSHAError("restored archive source route verification failed")
    os.replace(temp, target)
    return target
