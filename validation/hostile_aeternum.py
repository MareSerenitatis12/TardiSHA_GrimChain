#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from TardiSHA.alqc_digest import alqc_digest
from TardiSHA.domus_stream import living_domus_for_source
from TardiSHA.hashing import file_emission
from TardiSHA.mirror_math import mirror_file_emission


def body(index: int) -> bytes:
    seed = alqc_digest(
        f"ALQC Mirror emergence source {index}".encode(),
        domain=b"TARDISHA:HOSTILE-FIXTURE\x00",
        length=64,
    )
    return seed * ((index % 7) + 1) + index.to_bytes(4, "big") + bytes(range(index % 64)) + b"\x00\xff\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sources", type=int, default=32)
    parser.add_argument("--lineage", type=int, default=16)
    args = parser.parse_args()
    if args.sources < 2 or args.lineage < 1:
        raise SystemExit("--sources must be at least 2 and --lineage must be positive")

    checks = []
    def check(name: str, condition: bool, details=None):
        checks.append({"name": name, "pass": bool(condition), "details": details})

    with tempfile.TemporaryDirectory() as td:
        directory = Path(td)
        seals = []
        exact_fixed = exact_folded = mutated_rejected = mutated_changed = 0
        distinct_tested = distinct_rejected = equal_identity = 0

        for index in range(args.sources):
            path = directory / f"source_{index:04d}.bin"
            original = body(index)
            path.write_bytes(original)
            raw = file_emission(path)
            seal = living_domus_for_source(path, 0, kind="file")
            seals.append(seal)

            path.write_bytes(original + seal.encode("utf-8") + b"\n")
            mirrored = mirror_file_emission(path)
            second = living_domus_for_source(path, 0, kind="file")
            exact_fixed += second == seal
            exact_folded += (
                mirrored.witness.folded
                and mirrored.witness.fold_count == 1
                and mirrored.witness.source_route_dcomp == 0
                and mirrored.witness.source_truth == 1
                and mirrored.witness.return_dcomp == 0
                and mirrored.witness.return_truth == 1
                and mirrored.emission == raw
            )

            codepoints = list(seal)
            codepoints[1] = "⬡" if codepoints[1] != "⬡" else "⧗"
            mutated = "".join(codepoints)
            path.write_bytes(original + mutated.encode("utf-8") + b"\n")
            mutation = mirror_file_emission(path)
            mutated_rejected += not mutation.witness.folded and mutation.witness.return_truth == 0
            mutated_changed += mutation.emission != raw

            if index:
                foreign = seals[index - 1]
                if foreign == seal:
                    equal_identity += 1
                else:
                    distinct_tested += 1
                    path.write_bytes(original + foreign.encode("utf-8") + b"\n")
                    distinct_rejected += not mirror_file_emission(path).witness.folded

        lineage_path = directory / "lineage.bin"
        lineage_path.write_bytes(body(999))
        lineage_seal = living_domus_for_source(lineage_path, 0, kind="file")
        for _ in range(args.lineage):
            with lineage_path.open("ab") as handle:
                handle.write(lineage_seal.encode("utf-8") + b"\n")
        lineage_witness = mirror_file_emission(lineage_path)
        lineage_output = living_domus_for_source(lineage_path, 0, kind="file")

    check("all exact selves reach fixed point", exact_fixed == args.sources, exact_fixed)
    check("all exact selves fold by measured relation", exact_folded == args.sources, exact_folded)
    check("all one-code-point false returns remain source matter", mutated_rejected == args.sources, mutated_rejected)
    check("all false returns alter effective emission", mutated_changed == args.sources, mutated_changed)
    check("all distinct foreign compressed returns remain source matter", distinct_rejected == distinct_tested, {"tested": distinct_tested, "rejected": distinct_rejected, "equal_identity_encounters": equal_identity})
    check("compressed selves are source-derived rather than constant", len(set(seals)) > 1, len(set(seals)))
    check("append-only lineage folds without configured ceiling", lineage_witness.witness.fold_count == args.lineage and lineage_output == lineage_seal, lineage_witness.witness.fold_count)
    check("append-only physical ledger closes", lineage_witness.witness.bytes_accounted and lineage_witness.witness.return_dcomp == 0 and lineage_witness.witness.return_truth == 1)

    report = {"suite": "Aeternum Mirror hostile audit", "sources": args.sources, "lineage": args.lineage, "passed": sum(row["pass"] for row in checks), "failed": sum(not row["pass"] for row in checks), "checks": checks}
    target = ROOT / "validation" / "results" / "hostile_aeternum.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
