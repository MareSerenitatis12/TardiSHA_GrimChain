# Python API Guide

The command line is the simplest entry point, but the same implementation is available as a Python package.

## Seal and verify a file

```python
from TardiSHA import create_file, verify_file

seal = create_file("sample.bin", middle_length=31)
print(seal.value)
assert verify_file(seal.value, "sample.bin")
```

## Create a source-bound node

```python
from TardiSHA import node_from_file

node = node_from_file("sample.bin", mode="MANIFEST_FINITE", finite_extent=31)
print(node.node_id)
print(node.origin_glyph, node.resolution_glyph)
print(node.route_witness.route_dcomp)
print(node.route_witness.truth)
```

`MANIFEST_FINITE` requires `finite_extent` explicitly. `INVARIANT` materializes
only `⛎` and has no window API. `MANIFEST_OPEN` accepts requested finite windows
without storing or implying a terminal extent. `ARCHIVE_REVERSIBLE` is created by
the archive API only after a raw-file return proof and mandatory archive root exist.

## Inspect the Aeternum Mirror return

```python
from TardiSHA import aeternum_mirror_file_emission

result = aeternum_mirror_file_emission("sample.bin")
witness = result.witness

print(witness.physical_size)
print(witness.effective_body_size)
print(witness.folded)
print(witness.source_route_dcomp, witness.source_truth)
print(witness.return_dcomp, witness.return_truth)
```

For an ordinary file with no terminal returned Grimchain, `return_dcomp` and `return_truth` have no return verdict. For an exact terminal self-return they are `0` and `1`. For a parseable false return, return D-COMP is positive and return Truth is `0`.

## Generate a Living Domus value

```python
from pathlib import Path
from TardiSHA.domus_stream import living_domus_for_source

value = living_domus_for_source(Path("sample.bin"), 64, kind="file")
print(value)
```

Use depth `0` for the compressed Supervenience center and a positive integer for a Synodic Magicae center.

## Reversible archive

```python
from TardiSHA import create_archive, restore_archive

manifest = create_archive("sample.bin", "archive-directory", chunk_size=1024 * 1024)
print(manifest.archive_root)
restore_archive(
    "archive-directory/manifest.json",
    "archive-directory",
    "restored.bin",
)
```

The archive preserves physical bytes. A terminal returned self that occupies the Mirror return office is still restored exactly as stored.

## Complete public surface

`TardiSHA/__init__.py` exports the supported public names. `docs/MODULE_MAP.md` explains the internal module boundaries. Code using private underscore-prefixed functions should be treated as implementation-specific.

## Exact decision bodies

```python
from TardiSHA.aeon_layers import PHI, PHI_SQUARED, PHI_IMAGE
from TardiSHA.manifestation import C_BIO_SQUARED, exact_dcomp, exact_ennead_ledger

assert (PHI.a, PHI.b, PHI.denominator) == (1, 1, 2)
assert str(C_BIO_SQUARED) == "61009/44"
assert exact_ennead_ledger(3).energy_conserved
```

`PHI_IMAGE` is a display projection. Use the exact bodies for admission, conservation, and closure decisions.
