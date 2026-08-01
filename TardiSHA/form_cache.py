"""Q0-indexed, Q1-rewitnessed Form cache for TardiSHA file emissions.

The filesystem signature locates a possible entry. It never proves source truth.
Every hit re-witnesses the present file body, verifies the stored emission and route,
and proves that the source signature remained unchanged across the read.
"""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Final

from .hashing import TardiSHAError, validate_nonce
from .mirror_math import _signature, mirror_file_emission
from .route import SourceRouteWitness, verify_source
from .source_emission import SourceEmission

CACHE_VERSION: Final[int] = 2
CACHE_FILENAME: Final[str] = ".tardisha-form-cache.json"
_REQUIRED_ENTRY_FIELDS: Final[frozenset[str]] = frozenset({
    "path",
    "signature_before",
    "signature_after",
    "nonce",
    "emission",
    "route_witness",
})


def cache_path_for(target: str | Path) -> Path:
    source = Path(target).expanduser().resolve()
    root = source if source.is_dir() else source.parent
    return root / CACHE_FILENAME


def _key_from_signature(source: Path, signature: tuple[int, int, int], nonce: int) -> str:
    size, mtime_ns, inode = signature
    return f"{source}|{size}|{mtime_ns}|{inode}|{nonce}"


def signature_key(path: str | Path, *, nonce: int = 0) -> str:
    source = Path(path).expanduser().resolve()
    salt = validate_nonce(nonce)
    return _key_from_signature(source, _signature(source), salt)


def _validate_signature_body(value: object, *, field: str) -> tuple[int, int, int]:
    if not isinstance(value, list) or len(value) != 3:
        raise TardiSHAError(f"cache {field} must contain exactly three integers")
    if any(isinstance(item, bool) or not isinstance(item, int) or item < 0 for item in value):
        raise TardiSHAError(f"cache {field} must contain non-negative non-Boolean integers")
    return value[0], value[1], value[2]


def _validate_entry_metadata(key: str, body: dict[str, Any]) -> tuple[str, tuple[int, int, int], int]:
    path = body.get("path")
    if not isinstance(path, str) or not path:
        raise TardiSHAError(f"cache entry {key!r} path must be a non-empty string")
    nonce = body.get("nonce")
    try:
        salt = validate_nonce(nonce)
    except (TypeError, ValueError) as exc:
        raise TardiSHAError(f"cache entry {key!r} nonce is invalid") from exc
    before = _validate_signature_body(body.get("signature_before"), field="signature_before")
    after = _validate_signature_body(body.get("signature_after"), field="signature_after")
    if before != after:
        raise TardiSHAError(f"cache entry {key!r} does not preserve a stable source signature")
    return path, before, salt


def _decode_entry(key: str, body: dict[str, Any]) -> tuple[SourceEmission, SourceRouteWitness]:
    if set(body) != _REQUIRED_ENTRY_FIELDS:
        missing = sorted(_REQUIRED_ENTRY_FIELDS - set(body))
        extra = sorted(set(body) - _REQUIRED_ENTRY_FIELDS)
        raise TardiSHAError(f"cache entry {key!r} fields mismatch; missing={missing}, extra={extra}")
    _validate_entry_metadata(key, body)
    try:
        emission = SourceEmission.from_dict(body["emission"])
        route = SourceRouteWitness.from_dict(body["route_witness"])
    except (KeyError, TypeError, ValueError) as exc:
        raise TardiSHAError(f"cache entry {key!r} cannot be reconstructed") from exc
    if route.emission != emission or not verify_source(emission, route):
        raise TardiSHAError(f"cache entry {key!r} contains a false Q1 route witness")
    return emission, route


class FormCache:
    """Atomic cache whose entries remain subordinate to present Q1 source truth."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path).expanduser().resolve()
        self._entries: dict[str, dict[str, Any]] = {}
        self._dirty = False
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        try:
            body = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise TardiSHAError(f"Form cache {self.path} cannot be read as valid JSON") from exc
        if not isinstance(body, dict):
            raise TardiSHAError("Form cache root must be an object")
        if body.get("version") != CACHE_VERSION:
            raise TardiSHAError(
                f"Form cache version must be exactly {CACHE_VERSION}; found {body.get('version')!r}"
            )
        entries = body.get("entries")
        if not isinstance(entries, dict):
            raise TardiSHAError("Form cache entries must be an object")
        loaded: dict[str, dict[str, Any]] = {}
        for key, value in entries.items():
            if not isinstance(key, str) or not isinstance(value, dict):
                raise TardiSHAError("Form cache keys must be strings and entries must be objects")
            _decode_entry(key, value)
            loaded[key] = dict(value)
        self._entries = loaded

    def get(self, source: str | Path, *, nonce: int = 0) -> tuple[SourceEmission, SourceRouteWitness] | None:
        source_path = Path(source).expanduser().resolve()
        salt = validate_nonce(nonce)
        before = _signature(source_path)
        key = _key_from_signature(source_path, before, salt)
        body = self._entries.get(key)
        if body is None:
            return None

        entry_path, entry_signature, entry_nonce = _validate_entry_metadata(key, body)
        if entry_path != str(source_path):
            raise TardiSHAError("cache entry path contradicts its lookup source")
        if entry_nonce != salt:
            raise TardiSHAError("cache entry nonce contradicts its lookup nonce")
        if entry_signature != before:
            raise TardiSHAError("cache entry metadata contradicts the Q0 lookup signature")

        cached_emission, route = _decode_entry(key, body)
        current_emission = mirror_file_emission(source_path, nonce=salt).emission
        after = _signature(source_path)
        if after != before:
            raise TardiSHAError("source changed while the cache hit was being Q1-rewitnessed")
        if current_emission != cached_emission:
            raise TardiSHAError("cache emission does not equal the present Q1 source truth")
        if route.emission != current_emission or not verify_source(current_emission, route):
            raise TardiSHAError("cache route does not verify against the present Q1 source truth")
        return current_emission, route

    def put(
        self,
        source: str | Path,
        emission: SourceEmission,
        route: SourceRouteWitness,
        *,
        nonce: int = 0,
    ) -> None:
        source_path = Path(source).expanduser().resolve()
        salt = validate_nonce(nonce)
        before = _signature(source_path)
        current_emission = mirror_file_emission(source_path, nonce=salt).emission
        after = _signature(source_path)
        if after != before:
            raise TardiSHAError("source changed while the cache entry was being Q1-witnessed")
        if emission != current_emission:
            raise TardiSHAError("put() refused a stale emission for the present source body")
        if route.emission != current_emission or not verify_source(current_emission, route):
            raise TardiSHAError("cache entry route does not verify against the present source emission")

        key = _key_from_signature(source_path, before, salt)
        self._entries[key] = {
            "path": str(source_path),
            "signature_before": list(before),
            "signature_after": list(after),
            "nonce": salt,
            "emission": current_emission.as_dict(),
            "route_witness": route.as_dict(),
        }
        self._dirty = True

    def save(self) -> None:
        if not self._dirty:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        body = {
            "version": CACHE_VERSION,
            "entries": self._entries,
        }
        fd, tmp_name = tempfile.mkstemp(
            prefix=f".{self.path.name}.", suffix=".part", dir=self.path.parent
        )
        tmp = Path(tmp_name)
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
                json.dump(body, handle, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(tmp, self.path)
            self._dirty = False
        except Exception:
            tmp.unlink(missing_ok=True)
            raise
