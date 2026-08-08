"""TardiSHA boundary seals and streaming file operations."""
from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from .hashing import (
    ALPHABET,
    CANONICAL_SOURCE_DOMAIN,
    DIRECTORY_SOURCE_DOMAIN,
    RAW_FILE_SOURCE_DOMAIN,
    TardiSHAError,
    canonical_emission,
    coordinate_seed,
    create_middle_from_fingerprint,
    directory_emission,
    file_emission,
    identity_material,
    iter_middle,
    validate_glyph,
    validate_middle_length,
    validate_nonce,
)
from .domus import ZERO_MIDDLE_GLYPH
from .route import HashRoute, SourceRouteWitness, calculate_route, verify_source
from .mirror_math import mirror_file_emission
from .source_emission import SourceEmission
from .alqc_digest import validate_digest_hex
from .stream import StreamReport, count_codepoints, write_accordion_stream
from .regia import iter_regia_middle, regia_middle


_SOURCE_DOMAIN_BYTES = {
    "canonical": CANONICAL_SOURCE_DOMAIN,
    "raw-file": RAW_FILE_SOURCE_DOMAIN,
    "directory": DIRECTORY_SOURCE_DOMAIN,
}

@dataclass(frozen=True, slots=True)
class TardiSHASeal:
    origin_glyph: str
    middle: str
    resolution_glyph: str
    nonce: int
    route: HashRoute | None = None
    source_digest: str | None = None
    source_size: int | None = None

    def __post_init__(self) -> None:
        validate_glyph(self.origin_glyph, "origin_glyph")
        validate_glyph(self.resolution_glyph, "resolution_glyph")
        validate_nonce(self.nonce)
        if type(self.middle) is not str or not self.middle:
            raise TardiSHAError("seal middle must be one non-empty string body")
        if self.middle != ZERO_MIDDLE_GLYPH:
            if ZERO_MIDDLE_GLYPH in self.middle:
                raise TardiSHAError("positive-depth middle cannot contain the Shadow Locus glyph ⛎")
            if any(character not in ALPHABET for character in self.middle):
                raise TardiSHAError("positive-depth middle must contain only Synodic Magicae")

        bound = (self.route, self.source_digest, self.source_size)
        if all(value is None for value in bound):
            return
        if any(value is None for value in bound):
            raise TardiSHAError("bound seals require route, source_digest, and source_size together")
        if not isinstance(self.route, SourceRouteWitness):
            raise TardiSHAError("bound seal route must be one exact SourceRouteWitness")
        if type(self.source_digest) is not str:
            raise TardiSHAError("bound seal source_digest must be a string")
        try:
            validate_digest_hex(self.source_digest, field="source_digest")
        except ValueError as exc:
            raise TardiSHAError(str(exc)) from exc
        if isinstance(self.source_size, bool) or not isinstance(self.source_size, int) or self.source_size < 0:
            raise TardiSHAError("bound seal source_size must be a non-negative integer")
        if not verify_source(self.route.emission, self.route):
            raise TardiSHAError("bound seal route does not return-verify")
        if (
            self.source_digest != self.route.source_digest
            or self.source_size != self.route.source_size
            or (self.origin_glyph, self.resolution_glyph) != self.route.pair
        ):
            raise TardiSHAError("bound seal contradicts its source route")
        try:
            source_domain = _SOURCE_DOMAIN_BYTES[self.route.source_domain]
        except KeyError as exc:
            raise TardiSHAError("bound seal route has an unknown source domain") from exc
        expected = ZERO_MIDDLE_GLYPH if self.middle_length == 0 else create_middle_from_fingerprint(
            source_digest=self.source_digest,
            source_size=self.source_size,
            origin_glyph=self.origin_glyph,
            resolution_glyph=self.resolution_glyph,
            middle_length=self.middle_length,
            nonce=self.nonce,
            source_domain=source_domain,
        )
        if self.middle != expected:
            raise TardiSHAError("seal value is unrelated to its claimed source proof")

    @property
    def value(self) -> str:
        return f"{self.origin_glyph}{self.middle}{self.resolution_glyph}"

    @property
    def middle_length(self) -> int:
        return 0 if self.middle == ZERO_MIDDLE_GLYPH else len(self.middle)

    @property
    def boundary_condition(self) -> str:
        return self.origin_glyph + self.resolution_glyph

    @property
    def return_path(self) -> str:
        return f"{self.origin_glyph}→{self.resolution_glyph}→Reflect {self.origin_glyph}"

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class TardiSHAWriteResult:
    output_path: str
    origin_glyph: str
    resolution_glyph: str
    nonce: int
    source_digest: str
    source_size: int
    report: StreamReport
    manifest_path: str | None = None

    @property
    def middle_length(self) -> int:
        return self.report.middle_length

    @property
    def boundary_condition(self) -> str:
        return self.origin_glyph + self.resolution_glyph

    @property
    def return_path(self) -> str:
        return f"{self.origin_glyph}→{self.resolution_glyph}→Reflect {self.origin_glyph}"

    def as_dict(self) -> dict[str, object]:
        return {
            "output_path": self.output_path,
            "origin_glyph": self.origin_glyph,
            "resolution_glyph": self.resolution_glyph,
            "nonce": self.nonce,
            "source_digest": self.source_digest,
            "source_size": self.source_size,
            "boundary_condition": self.boundary_condition,
            "return_path": self.return_path,
            "manifest_path": self.manifest_path,
            "stream": self.report.as_dict(),
        }


def _resolve_boundaries(
    emission: SourceEmission,
    origin_glyph: str | None,
    resolution_glyph: str | None,
) -> tuple[str, str, HashRoute]:
    """Resolve the Final Equation Z pair from the complete source emission."""
    if (origin_glyph is None) != (resolution_glyph is None):
        raise TardiSHAError("origin_glyph and resolution_glyph must be supplied together")
    route = calculate_route(emission)
    if origin_glyph is not None:
        supplied = (
            validate_glyph(origin_glyph, "origin_glyph"),
            validate_glyph(resolution_glyph, "resolution_glyph"),
        )
        lawful = route.pair
        if supplied != lawful:
            raise TardiSHAError(
                f"explicit parent pair {supplied} contradicts Final Equation Z pair {lawful}"
            )
    return route.origin_glyph, route.resolution_glyph, route


def create(
    material: Any,
    *,
    middle_length: int,
    origin_glyph: str | None = None,
    resolution_glyph: str | None = None,
    nonce: int = 0,
) -> TardiSHASeal:
    width = validate_middle_length(middle_length)
    salt = validate_nonce(nonce)
    emission, _source = canonical_emission(material)
    source_digest, source_size = emission.source_digest, emission.source_size
    origin, resolution, route = _resolve_boundaries(emission, origin_glyph, resolution_glyph)
    middle = ZERO_MIDDLE_GLYPH if width == 0 else create_middle_from_fingerprint(
        source_digest=source_digest,
        source_size=source_size,
        origin_glyph=origin,
        resolution_glyph=resolution,
        middle_length=width,
        nonce=salt,
        source_domain=CANONICAL_SOURCE_DOMAIN,
    )
    return TardiSHASeal(origin, middle, resolution, salt, route, source_digest, source_size)


def parse(value: str, *, nonce: int = 0) -> TardiSHASeal:
    if not isinstance(value, str) or len(value) < 3:
        raise TardiSHAError("TardiSHA seal must contain two glyph boundaries and a visible middle")
    origin, middle, resolution = value[0], value[1:-1], value[-1]
    validate_glyph(origin, "origin_glyph")
    validate_glyph(resolution, "resolution_glyph")
    if middle != ZERO_MIDDLE_GLYPH and any(character not in ALPHABET for character in middle):
        raise TardiSHAError(
            "TardiSHA middle must be either the Shadow Locus glyph ⛎ or Synodic Magicae code points"
        )
    salt = validate_nonce(nonce)
    return TardiSHASeal(origin, middle, resolution, salt, None)


def verify(
    value: str,
    material: Any,
    *,
    nonce: int = 0,
    origin_glyph: str | None = None,
    resolution_glyph: str | None = None,
) -> bool:
    try:
        parsed = parse(value, nonce=nonce)
        emission, _source = canonical_emission(material)
        source_digest, source_size = emission.source_digest, emission.source_size
        origin, resolution, _route = _resolve_boundaries(emission, origin_glyph, resolution_glyph)
        if parsed.origin_glyph != origin or parsed.resolution_glyph != resolution:
            return False
        expected = create(material, middle_length=parsed.middle_length, nonce=nonce)
        return value == expected.value
    except (TypeError, ValueError, TardiSHAError):
        return False


def verify_record(record: Mapping[str, Any]) -> bool:
    if not isinstance(record, Mapping):
        return False
    required = {
        "TardiSHA_id", "TardiSHA_nonce", "TardiSHA_middle_length",
        "origin_glyph", "resolution_glyph",
    }
    if not required.issubset(record):
        return False
    value = record["TardiSHA_id"]
    nonce = record["TardiSHA_nonce"]
    middle_length = record["TardiSHA_middle_length"]
    origin = record["origin_glyph"]
    resolution = record["resolution_glyph"]
    if type(value) is not str or type(origin) is not str or type(resolution) is not str:
        return False
    if isinstance(nonce, bool) or not isinstance(nonce, int):
        return False
    if isinstance(middle_length, bool) or not isinstance(middle_length, int) or middle_length < 0:
        return False
    try:
        parsed = parse(value, nonce=nonce)
    except (TypeError, ValueError, TardiSHAError):
        return False
    if parsed.middle_length != middle_length:
        return False
    return verify(
        value,
        identity_material(record),
        nonce=nonce,
        origin_glyph=origin,
        resolution_glyph=resolution,
    )



def create_file(
    path: str | Path,
    *,
    middle_length: int,
    nonce: int = 0,
) -> TardiSHASeal:
    """Create an in-memory TardiSHA from raw file bytes.

    Use :func:`write_file_seal` when the requested middle is very large.
    """
    width = validate_middle_length(middle_length)
    salt = validate_nonce(nonce)
    first = mirror_file_emission(path, nonce=salt)
    emission = first.emission
    source_digest, source_size = emission.source_digest, emission.source_size
    origin, resolution, route = _resolve_boundaries(emission, None, None)
    middle = ZERO_MIDDLE_GLYPH if width == 0 else create_middle_from_fingerprint(
        source_digest=source_digest,
        source_size=source_size,
        origin_glyph=origin,
        resolution_glyph=resolution,
        middle_length=width,
        nonce=salt,
        source_domain=RAW_FILE_SOURCE_DOMAIN,
    )
    seal = TardiSHASeal(
        origin,
        middle,
        resolution,
        salt,
        route,
        source_digest,
        source_size,
    )
    second = mirror_file_emission(path, nonce=salt)
    if second != first:
        raise TardiSHAError("source file changed during complete seal construction")
    return seal


def _verify_file_shadow_locus(parsed: TardiSHASeal, path: str | Path, *, nonce: int = 0) -> bool:
    emission = mirror_file_emission(path, nonce=nonce).emission
    origin, resolution, _route = _resolve_boundaries(emission, None, None)
    return (
        parsed.origin_glyph == origin
        and parsed.middle == ZERO_MIDDLE_GLYPH
        and parsed.resolution_glyph == resolution
    )


def verify_file(value: str, path: str | Path, *, nonce: int = 0) -> bool:
    try:
        salt = validate_nonce(nonce)
        parsed = parse(value, nonce=salt)
        before = mirror_file_emission(path, nonce=salt)
        emission = before.emission
        origin, resolution, route = _resolve_boundaries(emission, None, None)
        expected_middle = ZERO_MIDDLE_GLYPH if parsed.middle_length == 0 else create_middle_from_fingerprint(
            source_digest=emission.source_digest,
            source_size=emission.source_size,
            origin_glyph=origin,
            resolution_glyph=resolution,
            middle_length=parsed.middle_length,
            nonce=salt,
            source_domain=RAW_FILE_SOURCE_DOMAIN,
        )
        expected = TardiSHASeal(
            origin, expected_middle, resolution, salt, route,
            emission.source_digest, emission.source_size,
        )
        after = mirror_file_emission(path, nonce=salt)
        return before == after and value == expected.value
    except (OSError, TypeError, ValueError, TardiSHAError):
        return False



def create_directory(
    path: str | Path,
    *,
    middle_length: int,
    nonce: int = 0,
) -> TardiSHASeal:
    """Create an in-memory TardiSHA from a canonical directory tree."""
    width = validate_middle_length(middle_length)
    salt = validate_nonce(nonce)
    emission, entry_count = directory_emission(path)
    source_digest, source_size = emission.source_digest, emission.source_size
    origin, resolution, route = _resolve_boundaries(emission, None, None)
    middle = ZERO_MIDDLE_GLYPH if width == 0 else create_middle_from_fingerprint(
        source_digest=source_digest,
        source_size=source_size,
        origin_glyph=origin,
        resolution_glyph=resolution,
        middle_length=width,
        nonce=salt,
        source_domain=DIRECTORY_SOURCE_DOMAIN,
    )
    seal = TardiSHASeal(
        origin,
        middle,
        resolution,
        salt,
        route,
        source_digest,
        source_size,
    )
    confirmed, confirmed_count = directory_emission(path)
    if confirmed != emission or confirmed_count != entry_count:
        raise TardiSHAError("directory changed during complete seal construction")
    return seal


def _verify_directory_shadow_locus(parsed: TardiSHASeal, path: str | Path) -> bool:
    emission, _entry_count = directory_emission(path)
    origin, resolution, _route = _resolve_boundaries(emission, None, None)
    return (
        parsed.origin_glyph == origin
        and parsed.middle == ZERO_MIDDLE_GLYPH
        and parsed.resolution_glyph == resolution
    )


def verify_directory(value: str, path: str | Path, *, nonce: int = 0) -> bool:
    try:
        salt = validate_nonce(nonce)
        parsed = parse(value, nonce=salt)
        before, before_count = directory_emission(path)
        origin, resolution, route = _resolve_boundaries(before, None, None)
        expected_middle = ZERO_MIDDLE_GLYPH if parsed.middle_length == 0 else create_middle_from_fingerprint(
            source_digest=before.source_digest,
            source_size=before.source_size,
            origin_glyph=origin,
            resolution_glyph=resolution,
            middle_length=parsed.middle_length,
            nonce=salt,
            source_domain=DIRECTORY_SOURCE_DOMAIN,
        )
        expected = TardiSHASeal(
            origin, expected_middle, resolution, salt, route,
            before.source_digest, before.source_size,
        )
        after, after_count = directory_emission(path)
        return before == after and before_count == after_count and value == expected.value
    except (OSError, TypeError, ValueError, TardiSHAError):
        return False



def create_dir(path: str | Path, **kwargs) -> TardiSHASeal:
    """Alias for create_directory."""
    return create_directory(path, **kwargs)


def verify_dir(value: str, path: str | Path, **kwargs) -> bool:
    """Alias for verify_directory."""
    return verify_directory(value, path, **kwargs)


def write_directory_seal(
    source_path: str | Path,
    output_path: str | Path,
    *,
    middle_length: int,
    nonce: int = 0,
    manifest_path: str | Path | None = None,
) -> TardiSHAWriteResult:
    """Stream a canonical directory-tree TardiSHA to disk with bounded memory."""
    width = validate_middle_length(middle_length)
    salt = validate_nonce(nonce)
    source = Path(source_path)
    output = Path(output_path)
    if source.resolve() == output.resolve():
        raise TardiSHAError("source_path and output_path must be different paths")
    manifest = Path(manifest_path) if manifest_path is not None else None

    emission, entry_count = directory_emission(source)
    source_digest, source_size = emission.source_digest, emission.source_size
    origin, resolution, _route = _resolve_boundaries(emission, None, None)
    report, output_temp, manifest_temp = _write_stream_to_paths(
        output_path=output,
        manifest_path=manifest,
        origin=origin,
        resolution=resolution,
        source_digest=source_digest,
        source_size=source_size,
        middle_length=width,
        nonce=salt,
        source_domain=DIRECTORY_SOURCE_DOMAIN,
    )

    after_emission, after_entry_count = directory_emission(source)
    if after_emission != emission or after_entry_count != entry_count:
        output_temp.unlink(missing_ok=True)
        if manifest_temp is not None:
            manifest_temp.unlink(missing_ok=True)
        raise TardiSHAError("directory tree changed while TardiSHA was being written")

    os.replace(output_temp, output)
    if manifest is not None and manifest_temp is not None:
        os.replace(manifest_temp, manifest)
    return TardiSHAWriteResult(
        str(output),
        origin,
        resolution,
        salt,
        source_digest,
        source_size,
        report,
        str(manifest) if manifest is not None else None,
    )



def _compare_streamed_seal(
    seal_file: Path,
    emission: SourceEmission,
    *,
    nonce: int,
    source_domain: bytes,
) -> bool:
    total_codepoints = count_codepoints(seal_file)
    center_codepoints = total_codepoints - 2
    if center_codepoints < 1:
        return False
    origin, resolution, _route = _resolve_boundaries(emission, None, None)
    with seal_file.open("r", encoding="utf-8", newline="") as handle:
        matched = handle.read(1) == origin
        if center_codepoints == 1:
            middle = handle.read(1)
            if middle == ZERO_MIDDLE_GLYPH:
                matched = matched and True
            else:
                seed = coordinate_seed(
                    source_digest=emission.source_digest,
                    source_size=emission.source_size,
                    origin_glyph=origin,
                    resolution_glyph=resolution,
                    middle_length=1,
                    nonce=nonce,
                    source_domain=source_domain,
                )
                matched = matched and middle == regia_middle(seed, 1)
        else:
            width = validate_middle_length(center_codepoints)
            seed = coordinate_seed(
                source_digest=emission.source_digest,
                source_size=emission.source_size,
                origin_glyph=origin,
                resolution_glyph=resolution,
                middle_length=width,
                nonce=nonce,
                source_domain=source_domain,
            )
            for expected in iter_regia_middle(seed, width):
                if handle.read(len(expected)) != expected:
                    matched = False
                    break
        if handle.read(1) != resolution:
            matched = False
        if handle.read(1) != "":
            matched = False
    return matched

def verify_directory_seal(
    seal_path: str | Path,
    source_path: str | Path,
    *,
    nonce: int = 0,
) -> bool:
    """Verify one stable directory source and one stable streamed seal body."""
    try:
        salt = validate_nonce(nonce)
        seal_file = Path(seal_path)
        seal_before = file_emission(seal_file)
        source_before, count_before = directory_emission(source_path)
        matched = _compare_streamed_seal(
            seal_file,
            source_before,
            nonce=salt,
            source_domain=DIRECTORY_SOURCE_DOMAIN,
        )
        source_after, count_after = directory_emission(source_path)
        seal_after = file_emission(seal_file)
        return (
            matched
            and source_before == source_after
            and count_before == count_after
            and seal_before == seal_after
        )
    except (OSError, TypeError, ValueError, TardiSHAError, UnicodeError):
        return False



def _temporary_text_path(target: Path) -> tuple[Path, object]:
    target.parent.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="",
        delete=False,
        dir=target.parent,
        prefix=f".{target.name}.",
        suffix=".part",
    )
    return Path(handle.name), handle


def _write_stream_to_paths(
    *,
    output_path: Path,
    manifest_path: Path | None,
    origin: str,
    resolution: str,
    source_digest: str,
    source_size: int,
    middle_length: int,
    nonce: int,
    source_domain: bytes,
) -> tuple[StreamReport, Path, Path | None]:
    seed = coordinate_seed(
        source_digest=source_digest,
        source_size=source_size,
        origin_glyph=origin,
        resolution_glyph=resolution,
        middle_length=middle_length,
        nonce=nonce,
        source_domain=source_domain,
    )
    output_temp, output_handle = _temporary_text_path(output_path)
    manifest_temp: Path | None = None
    manifest_handle = None
    try:
        if manifest_path is not None:
            manifest_temp, manifest_handle = _temporary_text_path(manifest_path)
        with output_handle:
            report = write_accordion_stream(
                output_handle,
                origin_glyph=origin,
                resolution_glyph=resolution,
                middle_chunks=iter_regia_middle(seed, middle_length),
                middle_length=middle_length,
                seed=seed,
                packet_manifest=manifest_handle,
            )
            output_handle.flush()
            os.fsync(output_handle.fileno())
        if manifest_handle is not None:
            with manifest_handle:
                manifest_handle.flush()
                os.fsync(manifest_handle.fileno())
        return report, output_temp, manifest_temp
    except Exception:
        cleanup_errors: list[Exception] = []
        try:
            output_handle.close()
        except Exception as exc:
            cleanup_errors.append(exc)
        if manifest_handle is not None:
            try:
                manifest_handle.close()
            except Exception as exc:
                cleanup_errors.append(exc)
        if cleanup_errors:
            raise ExceptionGroup("seal cleanup failed", cleanup_errors)
        output_temp.unlink(missing_ok=True)
        if manifest_temp is not None:
            manifest_temp.unlink(missing_ok=True)
        raise


def write_material_seal(
    material: Any,
    output_path: str | Path,
    *,
    middle_length: int,
    origin_glyph: str | None = None,
    resolution_glyph: str | None = None,
    nonce: int = 0,
    manifest_path: str | Path | None = None,
) -> TardiSHAWriteResult:
    width = validate_middle_length(middle_length)
    salt = validate_nonce(nonce)
    emission, _source = canonical_emission(material)
    source_digest, source_size = emission.source_digest, emission.source_size
    origin, resolution, _route = _resolve_boundaries(emission, origin_glyph, resolution_glyph)
    output = Path(output_path)
    manifest = Path(manifest_path) if manifest_path is not None else None
    report, output_temp, manifest_temp = _write_stream_to_paths(
        output_path=output,
        manifest_path=manifest,
        origin=origin,
        resolution=resolution,
        source_digest=source_digest,
        source_size=source_size,
        middle_length=width,
        nonce=salt,
        source_domain=CANONICAL_SOURCE_DOMAIN,
    )
    os.replace(output_temp, output)
    if manifest is not None and manifest_temp is not None:
        os.replace(manifest_temp, manifest)
    return TardiSHAWriteResult(
        str(output), origin, resolution, salt, source_digest, source_size, report,
        str(manifest) if manifest is not None else None,
    )


def write_file_seal(
    source_path: str | Path,
    output_path: str | Path,
    *,
    middle_length: int,
    nonce: int = 0,
    manifest_path: str | Path | None = None,
) -> TardiSHAWriteResult:
    """Stream a raw-file TardiSHA to disk with bounded memory and atomic commit."""
    width = validate_middle_length(middle_length)
    salt = validate_nonce(nonce)
    source = Path(source_path)
    output = Path(output_path)
    if source.resolve() == output.resolve():
        raise TardiSHAError("source_path and output_path must be different files")
    manifest = Path(manifest_path) if manifest_path is not None else None

    emission = mirror_file_emission(source, nonce=salt).emission
    source_digest, source_size = emission.source_digest, emission.source_size
    origin, resolution, _route = _resolve_boundaries(emission, None, None)
    report, output_temp, manifest_temp = _write_stream_to_paths(
        output_path=output,
        manifest_path=manifest,
        origin=origin,
        resolution=resolution,
        source_digest=source_digest,
        source_size=source_size,
        middle_length=width,
        nonce=salt,
        source_domain=RAW_FILE_SOURCE_DOMAIN,
    )

    after_emission = mirror_file_emission(source, nonce=salt).emission
    if after_emission != emission:
        output_temp.unlink(missing_ok=True)
        if manifest_temp is not None:
            manifest_temp.unlink(missing_ok=True)
        raise TardiSHAError("source file changed while TardiSHA was being written")

    os.replace(output_temp, output)
    if manifest is not None and manifest_temp is not None:
        os.replace(manifest_temp, manifest)
    return TardiSHAWriteResult(
        str(output),
        origin,
        resolution,
        salt,
        source_digest,
        source_size,
        report,
        str(manifest) if manifest is not None else None,
    )


def verify_file_seal(
    seal_path: str | Path,
    source_path: str | Path,
    *,
    nonce: int = 0,
) -> bool:
    """Verify one stable raw-file source and one stable streamed seal body."""
    try:
        salt = validate_nonce(nonce)
        seal_file = Path(seal_path)
        seal_before = file_emission(seal_file)
        source_before = mirror_file_emission(source_path, nonce=salt)
        matched = _compare_streamed_seal(
            seal_file,
            source_before.emission,
            nonce=salt,
            source_domain=RAW_FILE_SOURCE_DOMAIN,
        )
        source_after = mirror_file_emission(source_path, nonce=salt)
        seal_after = file_emission(seal_file)
        return matched and source_before == source_after and seal_before == seal_after
    except (OSError, TypeError, ValueError, TardiSHAError, UnicodeError):
        return False

