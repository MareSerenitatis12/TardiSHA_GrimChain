"""grimchain — one command: content in, ALQC seal out.

Positional middle is USER-CHOSEN at call time (any non-negative integer):

    grimchain <N> <path>            # seal a file with an explicit N-character middle
    grimchain <path>                # Shadow Locus zero middle (⛎)
    echo -n "text" | grimchain <N>  # seal stdin with an N-character middle
    grimchain -c list.txt           # verify files against a checksum list
"""
from __future__ import annotations

import os
import sys
import json
import tempfile
from pathlib import Path
from argparse import ArgumentParser, SUPPRESS
from importlib.metadata import PackageNotFoundError, version as package_version

from .folding import self_compress_ladder, ladder_manifest
from .node import node_from_file, node_from_directory
from .hashing import SOURCE_CHUNK_BYTES, TardiSHAError
from .domus import parse_living_domus
from .manifest import (
    manifest_output_path,
    verify_grimchain_manifest,
    write_grimchain_manifest,
)
from .domus_stream import (
    living_domus_for_source,
    write_living_domus_seal,
    verify_living_domus_seal,
    verify_living_domus_value,
)


_MIDDLE_UNSET = object()


def living_domus_for_file(target: Path, middle: int, nonce: int = 0) -> str:
    """Emit the ALQC Living Domus seal (plan §7, §16) for a file.

    middle == 0 -> ⛎ Shadow Locus center (31 code points);
    middle  > 0 -> the native prefix-stable Synodic Magicae coordinate stream
                   (30 + middle code points, no ⛎). Exposure only; identity is
                   bound to the file digest.
    """
    return living_domus_for_source(target, middle, kind="file", nonce=nonce)


def _materialize(data: bytes) -> str:
    """Write one exact in-memory byte body to a temporary source file."""
    if not isinstance(data, bytes):
        raise TypeError("materialized source must be bytes")
    fd, tmp = tempfile.mkstemp(suffix=".grimchain")
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        return tmp
    except Exception:
        Path(tmp).unlink(missing_ok=True)
        raise


def _materialize_stream(reader) -> str:
    """Copy one binary stream exactly, with bounded memory and no normalization."""
    fd, tmp = tempfile.mkstemp(suffix=".grimchain")
    try:
        with os.fdopen(fd, "wb") as handle:
            while True:
                chunk = reader.read(SOURCE_CHUNK_BYTES)
                if not chunk:
                    break
                if not isinstance(chunk, (bytes, bytearray, memoryview)):
                    raise TypeError("grimchain stream must yield bytes")
                handle.write(bytes(chunk))
            handle.flush()
            os.fsync(handle.fileno())
        return tmp
    except Exception:
        Path(tmp).unlink(missing_ok=True)
        raise



BASIC_HELP = """usage:
  grimchain PATH
  grimchain NUMBER PATH
  grimchain --string "TEXT"
  grimchain NUMBER --string "TEXT"
  grimchain NUMBER PATH --manifest
  grimchain NUMBER -R DIRECTORY --manifest
  grimchain --help -a

NUMBER is chosen by you. It tells Grimchain how many Synodic Magicae characters to
place in the middle of the Grimchain. 64 is only an example. Leave NUMBER out
to use the Shadow Locus ⛎ middle.

basic use:
  grimchain PATH
      Grimchain one file or one directory.

  grimchain NUMBER PATH
      Grimchain one file or directory using the number of middle characters
      you choose.

  grimchain --string "TEXT"
  grimchain NUMBER --string "TEXT"
      Grimchain the exact UTF-8 content supplied by the quoted argument.
      The quotes belong to the shell and are not part of the source.

  grimchain NUMBER FILE --manifest
      Create manifest-FILENAME.grim, prepare its terminal THIS FILE line,
      append its exact same-width self-return, and print that same Grimchain.

  grimchain NUMBER DIRECTORY --manifest
      Create manifest-DIRECTORYNAME.grim for the files directly inside that
      directory, then append and print its exact same-width THIS FILE return.

  grimchain NUMBER -R DIRECTORY --manifest
      Create manifest-recurse-DIRECTORYNAME.grim for all subdirectories, then
      append and print its exact same-width THIS FILE return.
"""

ADVANCED_HELP = """usage:
  grimchain [NUMBER] PATH [OPTIONS]
  grimchain [NUMBER] --string "TEXT" [OPTIONS]

NUMBER is any non-negative whole number you choose. It controls how many
Synodic Magicae characters appear in the middle. 64 is an example, not a fixed size.
Leave NUMBER out to use the Shadow Locus ⛎ middle.

ordinary use:
  grimchain PATH
      Grimchain one file or directory with the Shadow Locus ⛎ middle.

  grimchain NUMBER PATH
  grimchain --middle NUMBER PATH
      Grimchain one file or directory with NUMBER middle characters.

  grimchain --string "TEXT"
  grimchain NUMBER --string "TEXT"
      Grimchain the exact UTF-8 content inside the quoted shell argument.
      No newline, trimming, normalization, or separate string algorithm is added.

  grimchain NUMBER PATH --output FILE
      Save the Grimchain in FILE instead of printing it.

  grimchain PATH --verify --output FILE
      Check that FILE is the correct Grimchain for PATH.

manifests:
  grimchain [NUMBER] FILE --manifest
      Create manifest-FILENAME.grim with a terminal THIS FILE self-return.
      The same selected middle is used and the same Grimchain is printed.

  grimchain [NUMBER] DIRECTORY --manifest
      Create manifest-DIRECTORYNAME.grim for direct files, append its exact
      same-width THIS FILE return, and print that return.

  grimchain [NUMBER] -R DIRECTORY --manifest
      Create manifest-recurse-DIRECTORYNAME.grim for the complete tree, append
      its exact same-width THIS FILE return, and print that return.

  grimchain [NUMBER] PATH --manifest --output FILE
      Write the self-returning manifest to the filename you choose and print
      the exact Grimchain stored under its terminal THIS FILE line.

  grimchain [NUMBER] PATH --manifest --verify --output FILE
      Recreate the manifest information and check it against FILE.

inspection and lists:
  grimchain SEAL --inspect
      Show the parts contained in one Grimchain.

  grimchain -c LIST
  grimchain --check LIST
      Check a list whose lines contain: GRIMCHAIN  PATH

input and optional controls:
  printf 'text' | grimchain [NUMBER]
      Grimchain text received through standard input.

  grimchain --binary PATH
      Use the file's exact bytes. This is the only file-body law; line endings are never normalized.

  grimchain PATH --nonce INTEGER
      Use the chosen integer to create another repeatable Grimchain for PATH.

  grimchain PATH --fold --span NUMBER --levels NUMBER
      Create the fold-ladder output for PATH. Both dimensions are explicit and required.

  grimchain PATH1 PATH2 DIRECTORY
      Grimchain several sources in one command.

information:
  grimchain --version
      Show the installed TardiSHA version.

  grimchain --help
      Show basic use.

  grimchain --help -a
      Show all commands.
"""


def _installed_version() -> str:
    try:
        return package_version("TardiSHA")
    except PackageNotFoundError as exc:
        raise TardiSHAError("installed TardiSHA package metadata is required for --version") from exc


def main() -> None:
    argv = sys.argv[1:]
    separator_index = argv.index("--") if "--" in argv else None
    if separator_index is None:
        parser_argv = argv
        protected_args: list[str] = []
    else:
        parser_argv = argv[:separator_index]
        protected_args = argv[separator_index + 1:]

    p = ArgumentParser(prog="grimchain", description="content in, ALQC seal out", add_help=False)
    p.add_argument("args", nargs="*",
                   help="[MIDDLE] [PATH] — omit MIDDLE for the Shadow Locus center (⛎); PATH omitted reads stdin")
    p.add_argument("-h", "--help", action="store_true", help=SUPPRESS)
    p.add_argument("-a", "--advanced", action="store_true", help=SUPPRESS)
    p.add_argument("--version", action="store_true", help=SUPPRESS)
    p.add_argument("--middle", type=int, default=SUPPRESS, help="explicit middle length")
    p.add_argument("--string", metavar="TEXT", help="Grimchain the exact UTF-8 bytes of one shell argument")
    p.add_argument("-c", "--check", metavar="LIST", help="verify files against a nonempty checksum list")
    p.add_argument("-b", "--binary", action="store_true", help="read exact bytes; this is the only file-body law")
    p.add_argument("--output", type=Path, help="write the seal or manifest to a file")
    p.add_argument("--verify", action="store_true", help="verify --output against its source")
    p.add_argument("--manifest", action="store_true", help="write a Grimchain source manifest")
    p.add_argument("-R", "--recursive", action="store_true", help="include nested files in a directory manifest")
    p.add_argument("--fold", action="store_true", help="emit the born-glyph fold ladder")
    p.add_argument("--span", type=int, default=SUPPRESS, help="explicit fold span length")
    p.add_argument("--levels", type=int, default=SUPPRESS, help="explicit fold level count")
    p.add_argument("--inspect", action="store_true", help="parse one seal value")
    p.add_argument("--nonce", type=int, default=0)
    a = p.parse_intermixed_args(parser_argv)

    try:
        raw_args = list(a.args)
        unprotected_args = raw_args

        option_conflicts = any((
            a.version, a.string is not None, a.check is not None, a.binary, a.output is not None,
            a.verify, a.manifest, a.recursive, a.fold, a.inspect,
            hasattr(a, "middle"), hasattr(a, "span"), hasattr(a, "levels"), bool(raw_args),
        ))
        if a.help:
            if option_conflicts:
                p.error("--help may be combined only with -a/--advanced")
            print(ADVANCED_HELP if a.advanced else BASIC_HELP, end="")
            return
        if a.advanced:
            p.error("-a/--advanced is used only with --help")
        if a.version:
            if any((a.string is not None, a.check is not None, a.binary, a.output is not None, a.verify,
                    a.manifest, a.recursive, a.fold, a.inspect, hasattr(a, "middle"),
                    hasattr(a, "span"), hasattr(a, "levels"), bool(raw_args))):
                p.error("--version cannot be combined with another mode or source")
            print(_installed_version())
            return

        middle_value: int | object = getattr(a, "middle", _MIDDLE_UNSET)
        middle_was_supplied = middle_value is not _MIDDLE_UNSET
        if unprotected_args and not middle_was_supplied:
            token = unprotected_args[0]
            if token.lstrip("+").isdigit():
                middle_value = int(token)
                middle_was_supplied = True
                unprotected_args = unprotected_args[1:]
        paths = unprotected_args + protected_args

        if a.recursive and not a.manifest:
            p.error("-R/--recursive is used only with --manifest")
        if hasattr(a, "span") != hasattr(a, "levels"):
            p.error("--span and --levels must be supplied together")
        if a.fold:
            if not hasattr(a, "span") or not hasattr(a, "levels"):
                p.error("--fold requires explicit --span and --levels")
            if a.verify or a.output is not None or a.manifest or a.inspect or a.check or a.string is not None:
                p.error("--fold cannot be combined with --verify, --output, --manifest, --inspect, --check, or --string")
        elif hasattr(a, "span") or hasattr(a, "levels"):
            p.error("--span and --levels are used only with --fold")

        if a.check:
            if any((paths, middle_was_supplied, a.string is not None, a.binary, a.output is not None,
                    a.verify, a.manifest, a.recursive, a.fold, a.inspect)):
                p.error("--check cannot be combined with another mode, source, or middle")
            sys.exit(_check_list(a.check, a.nonce))

        if a.inspect:
            if any((middle_was_supplied, a.string is not None, a.binary, a.output is not None, a.verify,
                    a.manifest, a.recursive, a.fold)):
                p.error("--inspect cannot be combined with another mode, output, or middle")
            if len(paths) != 1:
                p.error("--inspect requires exactly one seal value")
            print(json.dumps(_living_payload(parse_living_domus(paths[0])), ensure_ascii=False, indent=2))
            return

        if a.manifest:
            if a.string is not None or a.binary or a.fold or a.inspect:
                p.error("--manifest cannot be combined with --string, --binary, --fold, or --inspect")
            if len(paths) != 1:
                p.error("--manifest requires exactly one file or directory")

        if a.string is not None:
            if paths:
                p.error("--string cannot be combined with file or directory paths")
            if a.manifest or a.recursive or a.inspect or a.binary or a.fold:
                p.error("--string cannot be combined with --manifest, -R, --inspect, --binary, or --fold")

        if len(paths) > 1 and a.output is not None:
            p.error("one --output cannot receive multiple sources")
        if a.verify and not a.manifest and a.output is None:
            p.error("--verify requires --output for a seal file")

        if a.string is not None:
            tmp = _materialize(a.string.encode("utf-8"))
            try:
                if middle_was_supplied:
                    assert isinstance(middle_value, int)
                    out = _do_file(Path(tmp), middle_value, a, source_label="--string")
                else:
                    out = _do_file_shadow_locus(Path(tmp), a, source_label="--string")
                print(out)
                if a.verify and not bool(json.loads(out).get("valid", False)):
                    sys.exit(1)
            finally:
                os.unlink(tmp)
            return

        if a.manifest:
            target = Path(paths[0]).expanduser().resolve()
            if not target.exists():
                raise FileNotFoundError(f"does not exist: {paths[0]}")
            destination = manifest_output_path(target, a.output, a.recursive).resolve()
            if middle_was_supplied:
                assert isinstance(middle_value, int)
                manifest_middle = middle_value
            else:
                manifest_middle = 0
            if a.verify:
                valid = verify_grimchain_manifest(
                    target, destination, middle=manifest_middle, recursive=a.recursive,
                    nonce=a.nonce, cache=False,
                )
                print(json.dumps({"valid": valid, "manifest": str(destination), "source": str(target)},
                                 ensure_ascii=False))
                if not valid:
                    sys.exit(1)
                return
            manifest = write_grimchain_manifest(
                target, destination, middle=manifest_middle, recursive=a.recursive,
                nonce=a.nonce, cache=False,
            )
            print(manifest["THIS FILE"])
            return

        if not paths:
            if sys.stdin.isatty():
                p.error("path required (or pipe input)")
            tmp = _materialize_stream(sys.stdin.buffer)
            try:
                if middle_was_supplied:
                    assert isinstance(middle_value, int)
                    print(_do_file(Path(tmp), middle_value, a, source_label="<stdin>"))
                else:
                    print(_do_file_shadow_locus(Path(tmp), a, source_label="<stdin>"))
            finally:
                os.unlink(tmp)
            return

        listing = len(paths) > 1
        verify_failed = False
        for raw in paths:
            target = Path(raw).expanduser().resolve()
            if not target.exists():
                raise FileNotFoundError(f"does not exist: {raw}")
            if target.is_dir():
                if middle_was_supplied:
                    assert isinstance(middle_value, int)
                    out = _do_dir(target, middle_value, a)
                else:
                    out = _do_dir_shadow_locus(target, a)
            else:
                if middle_was_supplied:
                    assert isinstance(middle_value, int)
                    out = _do_file(target, middle_value, a, source_label=raw)
                else:
                    out = _do_file_shadow_locus(target, a, source_label=raw)
            print(f"{out}  {raw}" if listing and not (a.fold or a.verify) else out)
            if a.verify and not bool(json.loads(out).get("valid", False)):
                verify_failed = True
        if a.verify and verify_failed:
            sys.exit(1)

    except BrokenPipeError:
        try:
            sys.stdout.close()
        except Exception:
            pass
    except (TardiSHAError, FileNotFoundError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"grimchain: {exc}", file=sys.stderr)
        sys.exit(1)


def _do_file_shadow_locus(target: Path, a, *, source_label: str | None = None) -> str:
    """Dispatch an omitted middle argument through the Shadow Locus zero path."""
    if a.verify:
        if not a.output:
            raise TardiSHAError("--verify requires --output pointing to the seal file")
        return json.dumps({
            "valid": verify_living_domus_seal(a.output, target, kind="file", nonce=a.nonce),
            "source": str(target) if source_label is None else source_label,
        }, ensure_ascii=False)
    if a.fold:
        node = node_from_file(target, nonce=a.nonce)
        return json.dumps(
            ladder_manifest(self_compress_ladder(node, span_length=a.span, levels=a.levels)),
            ensure_ascii=False,
            indent=2,
        )
    if a.output:
        r = write_living_domus_seal(
            target,
            a.output,
            kind="file",
            middle_length=0,
            nonce=a.nonce,
        )
        return json.dumps(r, ensure_ascii=False, indent=2)
    return living_domus_for_source(target, 0, kind="file", nonce=a.nonce)


def _do_dir_shadow_locus(target: Path, a) -> str:
    """Dispatch an omitted middle argument through the Shadow Locus zero path."""
    if a.verify:
        if not a.output:
            raise TardiSHAError("--verify requires --output pointing to the seal file")
        return json.dumps({
            "valid": verify_living_domus_seal(a.output, target, kind="directory", nonce=a.nonce),
            "source": str(target),
        }, ensure_ascii=False)
    if a.fold:
        node = node_from_directory(target, nonce=a.nonce)
        return json.dumps(
            ladder_manifest(self_compress_ladder(node, span_length=a.span, levels=a.levels)),
            ensure_ascii=False,
            indent=2,
        )
    if a.output:
        r = write_living_domus_seal(
            target,
            a.output,
            kind="directory",
            middle_length=0,
            nonce=a.nonce,
        )
        return json.dumps(r, ensure_ascii=False, indent=2)
    return living_domus_for_source(target, 0, kind="directory", nonce=a.nonce)


def _do_file(target: Path, middle: int, a, *, source_label: str | None = None) -> str:
    if a.verify:
        if not a.output:
            raise TardiSHAError("--verify requires --output pointing to the seal file")
        return json.dumps({"valid": verify_living_domus_seal(a.output, target, kind="file", nonce=a.nonce),
                           "source": str(target) if source_label is None else source_label}, ensure_ascii=False)
    if a.fold:
        node = node_from_file(target, nonce=a.nonce)
        return json.dumps(ladder_manifest(self_compress_ladder(node, span_length=a.span, levels=a.levels)),
                          ensure_ascii=False, indent=2)
    if a.output:
        r = write_living_domus_seal(target, a.output, kind="file", middle_length=middle, nonce=a.nonce)
        return json.dumps(r, ensure_ascii=False, indent=2)
    # Default content-in / seal-out is the ALQC Living Domus seal (plan §16).
    return living_domus_for_file(target, middle, nonce=a.nonce)


def _do_dir(target: Path, middle: int, a) -> str:
    if a.verify:
        if not a.output:
            raise TardiSHAError("--verify requires --output pointing to the seal file")
        return json.dumps({"valid": verify_living_domus_seal(a.output, target, kind="directory", nonce=a.nonce),
                           "source": str(target)}, ensure_ascii=False)
    if a.fold:
        node = node_from_directory(target, nonce=a.nonce)
        return json.dumps(ladder_manifest(self_compress_ladder(node, span_length=a.span, levels=a.levels)),
                          ensure_ascii=False, indent=2)
    if a.output:
        r = write_living_domus_seal(target, a.output, kind="directory", middle_length=middle, nonce=a.nonce)
        return json.dumps(r, ensure_ascii=False, indent=2)
    # Default directory seal is the ALQC Living Domus seal (plan §16).
    return living_domus_for_source(target, middle, kind="directory", nonce=a.nonce)


def _check_list(list_path: str, nonce: int) -> int:
    """Verify a checksum list. Each line: '<seal>  <path>'. Returns process exit code."""
    lines = Path(list_path).read_text(encoding="utf-8").splitlines()
    failed = 0
    checked = 0
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(None, 1)
        if len(parts) != 2:
            print(f"grimchain: malformed line: {raw}", file=sys.stderr)
            failed += 1
            continue
        seal, fpath = parts[0], parts[1].strip()
        target = Path(fpath)
        try:
            ok = target.is_dir() and verify_living_domus_value(seal, target, kind="directory", nonce=nonce) \
                 or target.is_file() and verify_living_domus_value(seal, target, kind="file", nonce=nonce)
        except (TardiSHAError, OSError):
            ok = False
        checked += 1
        print(f"{fpath}: {'OK' if ok else 'FAILED'}")
        if not ok:
            failed += 1
    if checked == 0:
        print("grimchain: checksum list contains no verifiable entries", file=sys.stderr)
        return 1
    if failed:
        print(f"grimchain: {failed} of {checked} failed", file=sys.stderr)
        return 1
    return 0


def _living_payload(parsed) -> dict:
    """Structural inspection of a Living Domus seal (no source recomputation)."""
    return {
        "governing_goetic": parsed.governing_goetic,
        "hyperbolic_parent": parsed.hyperbolic_parent,
        "root_court_glyph": parsed.root_court_glyph,
        "alternating_court_glyph": parsed.alternating_court_glyph,
        "b_q_glyph": parsed.b_q_glyph,
        "v_glyphs": list(parsed.v_glyphs),
        "center": parsed.center,
        "depth": parsed.depth,
    }


if __name__ == "__main__":
    main()
