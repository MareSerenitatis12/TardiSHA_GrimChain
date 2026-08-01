#!/usr/bin/env python3
from __future__ import annotations

import importlib
from dataclasses import replace
from itertools import product
from pathlib import Path
from tempfile import TemporaryDirectory

from TardiSHA import qstate_glyphs as Q
from TardiSHA.domus import ZERO_MIDDLE_GLYPH
from TardiSHA.hashing import TardiSHAError, canonical_emission, identity_material
from TardiSHA.route import (
    SourceRouteWitness,
    calculate_route,
    resolve_parents,
    source_route_witness_from_digest,
    source_route_witness_from_emission,
    verify_source,
)
from TardiSHA.seal import (
    TardiSHASeal,
    create,
    verify_directory_seal,
    verify_file_seal,
    verify_record,
    write_directory_seal,
    write_file_seal,
)
import TardiSHA.seal as seal_module


def rejected(call) -> bool:
    try:
        call()
    except (TypeError, ValueError, TardiSHAError):
        return True
    return False


def main() -> int:
    for vector in product(range(4), repeat=4):
        glyphs = Q.q_vector_glyphs(vector)
        assert tuple(Q.value_of_glyph(glyph) for glyph in glyphs) == vector
        body = Q.derive_domus_q_body(f"Q{vector[0]}", vector)
        assert body.q_vector == vector and body.q_glyphs == glyphs
    for bad in ((True, 0, 0, 0), (1.0, 0, 0, 0), ("1", 0, 0, 0), (0, 0, 0), (0, 0, 0, 4)):
        assert rejected(lambda bad=bad: Q.q_vector_glyphs(bad))

    emission, _ = canonical_emission({"route": "exact", "value": 12})
    witness = source_route_witness_from_emission(emission)
    assert calculate_route(emission) == witness
    assert verify_source(emission, witness)
    assert SourceRouteWitness.from_dict(witness.as_dict()) == witness
    assert resolve_parents(emission, witness=witness)[2] == witness
    for supplied in ({}, [], 0, False, ""):
        assert rejected(lambda supplied=supplied: resolve_parents(emission, witness=supplied))
    assert rejected(lambda: resolve_parents(emission, witness=replace(witness, truth=0)))
    assert rejected(lambda: source_route_witness_from_digest(
        emission.source_digest, emission.source_size, emission.source_domain
    ))
    for field, bad in (
        ("origin_index", True),
        ("origin_index", 1.0),
        ("origin_index", "1"),
        ("source_q_vector", [1.0, 2, 3, 0]),
        ("source_q_vector", [True, 2, 3, 0]),
        ("derivation_proof", object()),
    ):
        route_body = witness.as_dict()
        route_body[field] = bad
        assert rejected(lambda route_body=route_body: SourceRouteWitness.from_dict(route_body))

    try:
        importlib.import_module("TardiSHA." + "root_" + "matrices")
    except ModuleNotFoundError:
        pass
    else:
        raise AssertionError("removed Matrix runtime still imports")

    material = {"record": "strict", "count": 7}
    zero = create(material, middle_length=0, nonce=0)
    positive = create(material, middle_length=23, nonce=0)
    assert zero.middle == ZERO_MIDDLE_GLYPH and zero.middle_length == 0
    assert len(positive.middle) == 23 and ZERO_MIDDLE_GLYPH not in positive.middle

    contradictions = (
        dict(origin_glyph="not-a-goetic", middle=positive.middle, resolution_glyph=positive.resolution_glyph,
             nonce=positive.nonce, route=positive.route, source_digest=positive.source_digest, source_size=positive.source_size),
        dict(origin_glyph=positive.origin_glyph, middle=positive.middle + ZERO_MIDDLE_GLYPH,
             resolution_glyph=positive.resolution_glyph, nonce=positive.nonce, route=positive.route,
             source_digest=positive.source_digest, source_size=positive.source_size),
        dict(origin_glyph=positive.origin_glyph, middle="x", resolution_glyph=positive.resolution_glyph,
             nonce=positive.nonce, route=positive.route, source_digest=positive.source_digest, source_size=positive.source_size),
        dict(origin_glyph=positive.origin_glyph, middle=positive.middle, resolution_glyph=positive.resolution_glyph,
             nonce=True, route=positive.route, source_digest=positive.source_digest, source_size=positive.source_size),
        dict(origin_glyph=positive.origin_glyph, middle=positive.middle, resolution_glyph=positive.resolution_glyph,
             nonce=positive.nonce, route=positive.route, source_digest=positive.source_digest,
             source_size=positive.source_size + 1),
        dict(origin_glyph=positive.origin_glyph, middle=positive.middle[::-1], resolution_glyph=positive.resolution_glyph,
             nonce=positive.nonce, route=positive.route, source_digest=positive.source_digest, source_size=positive.source_size),
    )
    for body in contradictions:
        assert rejected(lambda body=body: TardiSHASeal(**body))

    record_material = {"payload": "record body", "number": 19}
    record_seal = create(record_material, middle_length=11, nonce=0)
    record = {
        **record_material,
        "TardiSHA_id": record_seal.value,
        "TardiSHA_nonce": 0,
        "TardiSHA_middle_length": 11,
        "origin_glyph": record_seal.origin_glyph,
        "resolution_glyph": record_seal.resolution_glyph,
    }
    assert identity_material(record) == record_material
    assert verify_record(record)
    for mutation in (
        {key: value for key, value in record.items() if key != "TardiSHA_nonce"},
        {**record, "TardiSHA_nonce": True},
        {**record, "TardiSHA_nonce": 7.9},
        {**record, "TardiSHA_nonce": "0"},
        {**record, "TardiSHA_middle_length": "11"},
        {**record, "TardiSHA_id": 12},
    ):
        assert not verify_record(mutation)

    with TemporaryDirectory() as temporary:
        root = Path(temporary)
        source = root / "source.bin"
        source.write_bytes(bytes(range(128)) + b"ALQC exact source")
        tree = root / "tree"
        tree.mkdir()
        (tree / "a.bin").write_bytes(b"alpha")
        (tree / "empty").mkdir()
        file_seal = root / "file.seal"
        directory_seal = root / "directory.seal"
        write_file_seal(source, file_seal, middle_length=37, nonce=0)
        write_directory_seal(tree, directory_seal, middle_length=17, nonce=0)
        assert verify_file_seal(file_seal, source, nonce=0)
        assert verify_directory_seal(directory_seal, tree, nonce=0)

        original_count = seal_module.count_codepoints
        def mutate_seal(path: Path) -> int:
            count = original_count(path)
            Path(path).write_text(Path(path).read_text(encoding="utf-8") + "x", encoding="utf-8")
            return count
        seal_module.count_codepoints = mutate_seal
        try:
            assert not verify_file_seal(file_seal, source, nonce=0)
        finally:
            seal_module.count_codepoints = original_count
        write_file_seal(source, file_seal, middle_length=37, nonce=0)

        original_compare = seal_module._compare_streamed_seal
        def mutate_source(*args, **kwargs):
            result = original_compare(*args, **kwargs)
            source.write_bytes(source.read_bytes() + b"!")
            return result
        seal_module._compare_streamed_seal = mutate_source
        try:
            assert not verify_file_seal(file_seal, source, nonce=0)
        finally:
            seal_module._compare_streamed_seal = original_compare

        def mutate_directory(*args, **kwargs):
            result = original_compare(*args, **kwargs)
            (tree / "late.bin").write_bytes(b"late")
            return result
        seal_module._compare_streamed_seal = mutate_directory
        try:
            assert not verify_directory_seal(directory_seal, tree, nonce=0)
        finally:
            seal_module._compare_streamed_seal = original_compare

    print("final repair ledger: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
