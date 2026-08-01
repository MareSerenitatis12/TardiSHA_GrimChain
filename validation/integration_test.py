#!/usr/bin/env python3
from __future__ import annotations
import compileall, json, os, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from TardiSHA.alqc_digest import ALQCDigest, alqc_hexdigest
from TardiSHA.archive import create_archive, read_archive_manifest, restore_archive
from TardiSHA.canon import boundary_glyphs_from_digest, court_load, law
from TardiSHA.domus import ZERO_MIDDLE_GLYPH, parse_living_domus
from TardiSHA.domus_stream import living_domus_for_source, verify_living_domus_seal, verify_living_domus_value, write_living_domus_seal
from TardiSHA.hashing import CANONICAL_SOURCE_DOMAIN, RAW_FILE_SOURCE_DOMAIN, canonical_bytes, canonical_emission, directory_emission, file_emission
from TardiSHA.manifest import verify_grimchain_manifest, write_grimchain_manifest
from TardiSHA.node import node_from_directory, node_from_file, node_from_material
from TardiSHA.qstate_glyphs import derive_domus_q_body
from TardiSHA.route import calculate_route, source_route_witness_from_digest, verify_source
from TardiSHA.seal import create, create_directory, create_file, verify, verify_directory, verify_file, verify_file_seal, write_file_seal
from TardiSHA.source_emission import PARLIAMENT_ORDER


def check(name: str, condition: bool, details=None) -> dict:
    if not condition:
        raise AssertionError(name)
    return {"name": name, "pass": True, "details": details}


def main() -> int:
    rows = []
    rows.append(check("package compiles", compileall.compile_dir(ROOT / "TardiSHA", quiet=1, force=True)))

    material = {"truth": ["light", "way"], "n": 47, "raw": bytes((0, 255, 1))}
    emission, _source = canonical_emission(material)
    legacy = alqc_hexdigest(canonical_bytes(material), domain=CANONICAL_SOURCE_DOMAIN)
    rows.append(check("canonical digest compatibility preserved", emission.source_digest == legacy))
    route = calculate_route(emission)
    rows.append(check("canonical route closes", route.route_dcomp == 0 and route.truth == 1))
    rows.append(check("canonical exact intervals", route.first.interval_verifies and route.last.interval_verifies))
    rows.append(check("Mirror Math keeps Parliament order", route.first.operator_order == route.last.operator_order == PARLIAMENT_ORDER))
    rows.append(check("Court begins after pair", route.court_address == court_load(*route.pair)))
    rows.append(check("canonical witness verifies", verify_source(emission, route)))
    seal = create(material, middle_length=14)
    rows.append(check("canonical finite seal verifies", verify(seal.value, material)))
    zero_seal = create(material, middle_length=0)
    rows.append(check(
        "canonical zero middle is Shadow Locus",
        zero_seal.middle == ZERO_MIDDLE_GLYPH
        and zero_seal.middle_length == 0
        and verify(zero_seal.value, material),
    ))
    node = node_from_material(material, mode="MANIFEST_FINITE", finite_extent=14)
    rows.append(check("canonical node carries route", node.route_witness == route and bool(json.dumps(node.as_dict(), ensure_ascii=False))))
    rows.append(check("finite node stores exact extent", node.finite_extent == 14 and len(node.materialized_middle()) == 14))
    try:
        node_from_material(material, mode="MANIFEST_FINITE")
    except Exception:
        rows.append(check("finite mode rejects absent extent", True))
    else:
        raise AssertionError("finite mode accepted absent extent")
    invariant_node = node_from_material(material, mode="INVARIANT")
    rows.append(check("invariant body is exactly Shadow Locus", invariant_node.materialized_middle() == ZERO_MIDDLE_GLYPH))
    try:
        invariant_node.middle_window(0, 0)
    except Exception:
        rows.append(check("invariant rejects window API", True))
    else:
        raise AssertionError("invariant admitted window derivation")
    open_node = node_from_material(material, mode="MANIFEST_OPEN")
    rows.append(check("open node has no terminal claim", open_node.finite_extent is None and len(open_node.middle_window(37, 9)) == 9))

    try:
        boundary_glyphs_from_digest(emission.source_digest)
    except ValueError:
        rows.append(check("Canon rejects digest-only parents", True))
    else:
        raise AssertionError("Canon accepts digest-only parents")

    try:
        source_route_witness_from_digest(emission.source_digest, emission.source_size, "canonical")
    except ValueError:
        rows.append(check("route rejects digest-only witness", True))
    else:
        raise AssertionError("route accepts digest-only witness")

    route_text = (ROOT / "TardiSHA" / "route.py").read_text(encoding="utf-8")
    emission_text = (ROOT / "TardiSHA" / "source_emission.py").read_text(encoding="utf-8")
    rows.append(check("no endpoint byte selector", "raw[0]" not in route_text and "raw[31]" not in route_text and " % 12" not in route_text))
    rows.append(check("no reverse Parliament procession", "reversed(range(12))" not in emission_text and "tuple(reversed" not in emission_text))

    with tempfile.TemporaryDirectory() as td:
        directory = Path(td)
        source_path = directory / "source.bin"
        source_path.write_bytes(bytes(range(256)) * 19 + b"FINAL-EQUATION-Z")
        file_result = file_emission(source_path)
        raw = ALQCDigest(RAW_FILE_SOURCE_DOMAIN)
        raw._update_raw(source_path.read_bytes())
        rows.append(check("raw-file digest compatibility preserved", file_result.source_digest == raw.hexdigest()))
        file_route = calculate_route(file_result)
        file_node = node_from_file(source_path, mode="MANIFEST_FINITE", finite_extent=31)
        rows.append(check("file node carries exact route", file_node.route_witness == file_route))
        file_seal = create_file(source_path, middle_length=31)
        rows.append(check("file finite seal verifies", verify_file(file_seal.value, source_path)))
        file_zero = create_file(source_path, middle_length=0)
        rows.append(check(
            "file zero middle is Shadow Locus",
            file_zero.middle == ZERO_MIDDLE_GLYPH
            and file_zero.middle_length == 0
            and verify_file(file_zero.value, source_path),
        ))
        simple_zero_path = directory / "simple-zero.seal"
        write_file_seal(source_path, simple_zero_path, middle_length=0)
        rows.append(check(
            "streamed simple zero seal writes and verifies Shadow Locus",
            ZERO_MIDDLE_GLYPH in simple_zero_path.read_text(encoding="utf-8")
            and verify_file_seal(simple_zero_path, source_path),
        ))
        mutation = directory / "mutation.bin"
        mutation.write_bytes(source_path.read_bytes() + b"!")
        rows.append(check("mutated file rejected", not verify_file(file_seal.value, mutation)))
        visible = living_domus_for_source(source_path, 31, kind="file")
        rows.append(check("visible Domus verifies", verify_living_domus_value(visible, source_path, kind="file")))
        visible_parsed = parse_living_domus(visible)
        governing = law(file_route.pair[0])
        expected_q_body = derive_domus_q_body(governing.q_bias, governing.q_vector)
        rows.append(check("visible Domus bias derives from the resolved governing Court",
                          visible_parsed.b_q_glyph == expected_q_body.bias_glyph))
        rows.append(check("visible Domus Q-body derives in exact vector order",
                          visible_parsed.v_glyphs == expected_q_body.q_glyphs))
        stream_path = directory / "stream.seal"
        write_living_domus_seal(source_path, stream_path, kind="file", middle_length=31)
        rows.append(check("streamed file seal byte-exact", stream_path.read_text(encoding="utf-8") == visible))
        rows.append(check("streamed file seal verifies", verify_living_domus_seal(stream_path, source_path, kind="file")))

        tree = directory / "tree"
        tree.mkdir()
        (tree / "a.txt").write_text("alpha", encoding="utf-8")
        (tree / "empty").mkdir()
        (tree / "sub").mkdir()
        (tree / "sub" / "b.bin").write_bytes(b"beta\0gamma")
        directory_result, entries = directory_emission(tree)
        directory_route = calculate_route(directory_result)
        directory_node = node_from_directory(tree, mode="MANIFEST_FINITE", finite_extent=17)
        rows.append(check("directory entry count", entries == 5, entries))
        rows.append(check("directory node carries exact route", directory_node.route_witness == directory_route))
        directory_seal = create_directory(tree, middle_length=17)
        rows.append(check("directory finite seal verifies", verify_directory(directory_seal.value, tree)))
        directory_stream = directory / "directory.seal"
        write_living_domus_seal(tree, directory_stream, kind="directory", middle_length=17)
        rows.append(check("streamed directory seal verifies", verify_living_domus_seal(directory_stream, tree, kind="directory")))

        archive = directory / "archive"
        manifest = create_archive(source_path, archive, chunk_size=113)
        rows.append(check(
            "archive node is rooted at construction",
            manifest.node.archive_root == manifest.archive_root
            and manifest.node.mode == "ARCHIVE_REVERSIBLE"
            and manifest.node.source_domain == "raw-file"
            and manifest.node.mode_witness()["exact_return_bearing_source_proof"],
        ))
        try:
            node_from_file(source_path, mode="ARCHIVE_REVERSIBLE", mirror_self=False)
        except Exception:
            rows.append(check("archive mode rejects absent root", True))
        else:
            raise AssertionError("archive mode accepted absent root")
        try:
            node_from_file(source_path, mode="MANIFEST_OPEN", mirror_self=False)
        except Exception:
            rows.append(check("mirror bypass rejected outside archive", True))
        else:
            raise AssertionError("mirror_self=False escaped archive boundary")
        try:
            node_from_material(material, mode="ARCHIVE_REVERSIBLE")
        except Exception:
            rows.append(check("archive mode rejects canonical material", True))
        else:
            raise AssertionError("archive mode accepted canonical material")
        try:
            node_from_directory(tree, mode="ARCHIVE_REVERSIBLE")
        except Exception:
            rows.append(check("archive mode rejects directory source", True))
        else:
            raise AssertionError("archive mode accepted directory source")
        reread = read_archive_manifest(archive / "manifest.json")
        restored = directory / "restored.bin"
        restore_archive(archive / "manifest.json", archive, restored)
        rows.append(check("archive root stable", manifest.archive_root == reread.archive_root))
        rows.append(check("archive route witness stable", reread.node.route_witness == file_node.route_witness))
        rows.append(check("archive restores bytes", restored.read_bytes() == source_path.read_bytes()))

        command = ROOT / "grimchain"
        process = subprocess.run([str(command), str(source_path)], cwd=ROOT, capture_output=True, text=True, env={**os.environ, "PYTHONPATH": str(ROOT)})
        rows.append(check("local grimchain exits zero", process.returncode == 0, process.stderr))
        parsed = parse_living_domus(process.stdout.strip())
        rows.append(check("local grimchain exposes derived pair", (parsed.governing_goetic, parsed.hyperbolic_parent) == file_route.pair))

        exact_string = "Quoted string ✦ with spaces and $HOME"
        exact_string_path = directory / "exact-string.txt"
        exact_string_path.write_bytes(exact_string.encode("utf-8"))
        newline_string_path = directory / "exact-string-newline.txt"
        newline_string_path.write_bytes(exact_string.encode("utf-8") + b"\n")
        string_compact = subprocess.run(
            [str(command), "--string", exact_string], cwd=ROOT, capture_output=True, text=True,
            env={**os.environ, "PYTHONPATH": str(ROOT)},
        )
        string_depth = subprocess.run(
            [str(command), "37", "--string", exact_string], cwd=ROOT, capture_output=True, text=True,
            env={**os.environ, "PYTHONPATH": str(ROOT)},
        )
        empty_string = subprocess.run(
            [str(command), "--string", ""], cwd=ROOT, capture_output=True, text=True,
            env={**os.environ, "PYTHONPATH": str(ROOT)},
        )
        empty_path = directory / "empty-string.txt"
        empty_path.write_bytes(b"")
        nonce_string = subprocess.run(
            [str(command), "29", "--string", exact_string, "--nonce", "42"], cwd=ROOT,
            capture_output=True, text=True, env={**os.environ, "PYTHONPATH": str(ROOT)},
        )
        string_output_path = directory / "quoted-string.grim"
        string_output = subprocess.run(
            [str(command), "17", "--string", exact_string, "--output", str(string_output_path)],
            cwd=ROOT, capture_output=True, text=True,
            env={**os.environ, "PYTHONPATH": str(ROOT)},
        )
        string_verify = subprocess.run(
            [str(command), "17", "--string", exact_string, "--verify", "--output", str(string_output_path)],
            cwd=ROOT, capture_output=True, text=True,
            env={**os.environ, "PYTHONPATH": str(ROOT)},
        )
        string_wrong_verify = subprocess.run(
            [str(command), "17", "--string", exact_string + "!", "--verify", "--output", str(string_output_path)],
            cwd=ROOT, capture_output=True, text=True,
            env={**os.environ, "PYTHONPATH": str(ROOT)},
        )
        rows.append(check(
            "--string Grimchains exact UTF-8 content without adding a newline",
            string_compact.returncode == 0
            and string_compact.stdout.strip() == living_domus_for_source(exact_string_path, 0, kind="file")
            and string_compact.stdout.strip() != living_domus_for_source(newline_string_path, 0, kind="file"),
            string_compact.stderr,
        ))
        rows.append(check(
            "--string preserves the explicit user middle",
            string_depth.returncode == 0
            and parse_living_domus(string_depth.stdout.strip()).depth == 37
            and string_depth.stdout.strip() == living_domus_for_source(exact_string_path, 37, kind="file"),
            string_depth.stderr,
        ))
        rows.append(check(
            "--string accepts an empty quoted argument",
            empty_string.returncode == 0
            and empty_string.stdout.strip() == living_domus_for_source(empty_path, 0, kind="file"),
            empty_string.stderr,
        ))
        rows.append(check(
            "--string preserves the ordinary nonce rule",
            nonce_string.returncode == 0
            and nonce_string.stdout.strip() == living_domus_for_source(exact_string_path, 29, kind="file", nonce=42),
            nonce_string.stderr,
        ))
        rows.append(check(
            "--string preserves ordinary output and verification",
            string_output.returncode == 0
            and string_output_path.exists()
            and string_verify.returncode == 0
            and json.loads(string_verify.stdout)["valid"] is True,
            {"output": string_output.stderr, "verify": string_verify.stderr},
        ))
        rows.append(check(
            "--string verification rejects different quoted content",
            string_wrong_verify.returncode == 1
            and json.loads(string_wrong_verify.stdout)["valid"] is False,
            string_wrong_verify.stderr,
        ))

        manifest_path = directory / "manifest-source.bin.grim"
        manifest_result = write_grimchain_manifest(source_path, manifest_path, middle=19)
        manifest_bytes = manifest_path.read_bytes()
        this_file_marker = b"\nTHIS FILE\n"
        marker_at = manifest_bytes.rfind(this_file_marker)
        stored_self = manifest_bytes[marker_at + len(this_file_marker):-1].decode("utf-8")
        rows.append(check(
            "manifest prepares THIS FILE before appending only its Grimchain",
            marker_at >= 0
            and manifest_bytes.endswith(stored_self.encode("utf-8") + b"\n")
            and manifest_result["THIS FILE"] == stored_self,
        ))
        rows.append(check(
            "manifest THIS FILE preserves the user-chosen middle",
            parse_living_domus(stored_self).depth == 19,
        ))
        prepared_manifest = directory / "prepared-manifest.grim"
        prepared_manifest.write_bytes(manifest_bytes[:marker_at + len(this_file_marker)])
        rows.append(check(
            "prepared manifest Grimchain equals stored THIS FILE",
            living_domus_for_source(prepared_manifest, 19, kind="file") == stored_self,
        ))
        rows.append(check(
            "completed manifest Grimchain equals stored THIS FILE",
            living_domus_for_source(manifest_path, 19, kind="file") == stored_self,
        ))
        rows.append(check(
            "manifest verifier accepts the exact same-width self-return",
            verify_grimchain_manifest(source_path, manifest_path, middle=19),
        ))
        rows.append(check(
            "manifest verifier rejects a different requested middle",
            not verify_grimchain_manifest(source_path, manifest_path, middle=18),
        ))

        recursive_manifest = directory / "manifest-recurse-tree.grim"
        recursive_result = write_grimchain_manifest(tree, recursive_manifest, middle=23, recursive=True)
        rows.append(check(
            "recursive manifest records the complete selected tree",
            [entry["path"] for entry in recursive_result["entries"]]
            == [".", "a.txt", "empty", "sub", "sub/b.bin"],
        ))
        rows.append(check(
            "recursive manifest closes through its same-width THIS FILE return",
            verify_grimchain_manifest(tree, recursive_manifest, middle=23, recursive=True)
            and living_domus_for_source(recursive_manifest, 23, kind="file") == recursive_result["THIS FILE"],
        ))

        cli_manifest = directory / "cli-manifest-source.grim"
        manifest_process = subprocess.run(
            [str(command), "19", "--manifest", str(source_path), "--output", str(cli_manifest)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONPATH": str(ROOT)},
        )
        cli_stored = cli_manifest.read_bytes().split(this_file_marker, 1)[1][:-1].decode("utf-8")
        rows.append(check(
            "manifest CLI prints the exact terminal THIS FILE Grimchain",
            manifest_process.returncode == 0 and manifest_process.stdout.strip() == cli_stored,
            manifest_process.stderr,
        ))

    report = {"suite": "TardiSHA public integration", "passed": len(rows), "failed": 0, "checks": rows}
    target = ROOT / "validation" / "results" / "integration_test.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
