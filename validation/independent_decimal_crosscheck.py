#!/usr/bin/env python3
from __future__ import annotations
import argparse
from decimal import Decimal, getcontext
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from TardiSHA.hashing import RAW_FILE_SOURCE_DOMAIN
from TardiSHA.route import calculate_route
from TardiSHA.source_emission import PARLIAMENT, PHASE_DENOMINATOR, emission_from_chunks

getcontext().prec = 140
D = Decimal
SQRT5 = D(5).sqrt()
ALPHA = (SQRT5 - D(1)) / D(2)
BETA = (D(3) - SQRT5) / D(2)
DENOMINATOR = D(PHASE_DENOMINATOR)


def source(index: int) -> bytes:
    return b"FINAL-EQUATION-Z-INDEPENDENT\0" + index.to_bytes(8, "big")


def owner(weights, phase, bearing):
    point = (D(phase) / DENOMINATOR + bearing) % D(1)
    total = D(sum(weights))
    cumulative = D(0)
    before = D(0)
    for index, weight in enumerate(weights):
        before = cumulative
        cumulative += D(weight) / total
        if point < cumulative:
            return PARLIAMENT[index].goetic, point, min(point - before, cumulative - point)
    raise AssertionError("decimal bearing escaped body")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sources", type=int, default=200)
    args = parser.parse_args()
    if args.sources < 1:
        raise SystemExit("--sources must be positive")

    minimum_margin = D(1)
    samples = []
    for index in range(args.sources):
        emission = emission_from_chunks((source(index),), source_domain_bytes=RAW_FILE_SOURCE_DOMAIN, source_domain="raw-file")
        route = calculate_route(emission)
        first, first_point, first_margin = owner(emission.structural_weights, emission.fraktur_z0, ALPHA)
        last, last_point, last_margin = owner(emission.operational_weights, emission.fraktur_z1, BETA)
        if (first, last) != route.pair:
            raise AssertionError(f"independent resolver mismatch at source {index}")
        minimum_margin = min(minimum_margin, first_margin, last_margin)
        if index < 8:
            samples.append({"index": index, "pair": [first, last], "first_point": str(first_point), "last_point": str(last_point), "minimum_interval_margin": str(min(first_margin, last_margin))})

    report = {"suite": "independent 140-digit Golden-bearing cross-check", "sources": args.sources, "all_match": True, "minimum_decimal_interval_margin": str(minimum_margin), "samples": samples}
    target = ROOT / "validation" / "results" / "independent_decimal_crosscheck.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
