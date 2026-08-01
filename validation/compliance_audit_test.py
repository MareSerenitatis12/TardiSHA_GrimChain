#!/usr/bin/env python3
"""Acceptance harness for the active ALQC compliance laws."""
from __future__ import annotations

import importlib
import json
import sys
import tempfile
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import TardiSHA.alqc_digest as AD
from TardiSHA import aeon_layers as AL
from TardiSHA import archive as AR
from TardiSHA import manifest as MF
from TardiSHA import manifestation as MN
from TardiSHA import tripartite as TP
from TardiSHA.hashing import TardiSHAError
from TardiSHA.source_emission import Q5Fraction

checks: list[dict[str, object]] = []


def check(name: str, condition: bool, details: object = None) -> None:
    checks.append({"name": name, "pass": bool(condition), "details": details})


check("Phi is exact Q(sqrt(5))", (AL.PHI.a, AL.PHI.b, AL.PHI.denominator) == (1, 1, 2))
check("Phi squared is exact Q(sqrt(5))", (AL.PHI_SQUARED.a, AL.PHI_SQUARED.b, AL.PHI_SQUARED.denominator) == (3, 1, 2))

ledger_cases = [MN.exact_ennead_ledger(value) for value in range(MN.SHADOW_CAPACITY + 1)]
ledger_cases.extend(
    MN.exact_ennead_ledger(value)
    for value in (Fraction(1, 7), Fraction(1, 2), Fraction(93, 7), Fraction(93, 2), Fraction(650, 7))
)
check(
    "Ennead conserves every declared finite debt body",
    all(item.energy_conserved and item.accounted_total == item.initial_debt and item.saturated for item in ledger_cases),
    len(ledger_cases),
)
check("Shadow capacity is the exact integer 93", MN.SHADOW_CAPACITY == 93 and isinstance(MN.SHADOW_CAPACITY, int))
check("C_bio identity is exact squared rational 61009/44", MN.C_BIO_SQUARED == Fraction(61009, 44))
check("Root frequency split remains symbolic by exact square", TP.AXIOMYR_BRANCH_COMPONENT_SQUARED == Fraction(1847, 200))
exact_route = MN.exact_dcomp((1, 1, 1, 3), (1, 2, 1, 3), court=0)
check(
    "Q-vector D-COMP retains exact rational and Q(sqrt(5)) bodies",
    isinstance(exact_route.velocity_mismatch_square, Fraction)
    and isinstance(exact_route.shadow_debt_initial, Q5Fraction),
)

violations: list[str] = []
for source in sorted((ROOT / "TardiSHA").glob("*.py")):
    for line_number, line in enumerate(source.read_text(encoding="utf-8").splitlines(), 1):
        if "isclose" in line or "1e-" in line:
            violations.append(f"{source.name}:{line_number}:{line.strip()}")
check("No tolerance decision remains", not violations, violations)

kernel_fixtures = (
    (0, 0), (1, 1), (2, 31), (3, 32), (5, 63), (8, 64),
    (13, 127), (21, 128), (34, 255), (55, 256), (89, 511), (144, 512),
)
kernel_ok = AD.COMPILED_KERNEL_ACTIVE and AD._compiled_absorb_raw is not None
kernel_failure = None
if kernel_ok:
    for seed, length in kernel_fixtures:
        data = bytes(((seed * 29 + index * 97 + index * index * 3) ^ (seed >> 2)) & 255 for index in range(length))
        first = AD.alqc_hexdigest(data)
        second = AD.alqc_hexdigest(data)
        if first != second or len(first) != AD.DIGEST_HEX_LENGTH:
            kernel_ok = False
            kernel_failure = {"seed": seed, "length": length, "first": first, "second": second}
            break
check("Compiled ALQC kernel closes fixed boundary fixtures", kernel_ok, kernel_failure)

try:
    importlib.import_module("TardiSHA." + "root_" + "matrices")
except ModuleNotFoundError:
    matrix_absent = True
else:
    matrix_absent = False
check("Matrix runtime module is absent", matrix_absent)

with tempfile.TemporaryDirectory() as temporary:
    root = Path(temporary)
    tree = root / "tree"
    tree.mkdir()
    (tree / "body.bin").write_bytes(b"manifest body")
    try:
        MF.build_grimchain_manifest(tree, middle=0, recursive=True, nonce=3, cache=True)
    except TardiSHAError:
        cache_rejected = True
    else:
        cache_rejected = False
    check("Manifest cache route is rejected", cache_rejected)

    source = root / "archive-source.bin"
    source.write_bytes(b"archive-body" * 64)
    store = root / "archive"
    manifest = AR.create_archive(source, store, chunk_size=64)
    first_chunk = store / "chunks" / f"{manifest.chunks[0].digest}.bin"
    first_chunk.write_bytes(first_chunk.read_bytes() + b"corrupt")
    try:
        AR.create_archive(source, store, chunk_size=64)
    except TardiSHAError:
        corrupted_chunk_rejected = True
    else:
        corrupted_chunk_rejected = False
    check("Existing archive chunks require content truth", corrupted_chunk_rejected)

report = {
    "suite": "TardiSHA ALQC Compliance acceptance",
    "passed": sum(bool(item["pass"]) for item in checks),
    "failed": sum(not bool(item["pass"]) for item in checks),
    "checks": checks,
}
print(json.dumps(report, ensure_ascii=False, indent=2))
raise SystemExit(0 if report["failed"] == 0 else 1)
