#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import os
import subprocess
import sys
import tempfile
import tarfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from TardiSHA.domus_stream import living_domus_for_source, verify_living_domus_value
RESULTS = ROOT / "validation" / "results"
RESULTS.mkdir(exist_ok=True)


def run(name: str, command: list[str], *, cwd: Path = ROOT, env=None) -> dict:
    process = subprocess.run(command, cwd=cwd, capture_output=True, text=True, env=env)
    record = {"name": name, "command": command, "returncode": process.returncode, "pass": process.returncode == 0, "stdout": process.stdout, "stderr": process.stderr}
    if process.returncode != 0:
        print(process.stdout)
        print(process.stderr, file=sys.stderr)
    return record


def grimchain_provenance(path: Path) -> str:
    return living_domus_for_source(path, 0, kind="file")


def verify_provenance_manifest() -> dict:
    manifest_path = ROOT / "SOURCE_GRIMCHAIN_MANIFEST.json"
    if not manifest_path.exists():
        return {
            "name": "release Grimchain provenance",
            "pass": False,
            "checked": 0,
            "failures": [{"error": "SOURCE_GRIMCHAIN_MANIFEST.json missing"}],
        }
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    failures = []
    checked = 0
    for entry in manifest.get("entries", []):
        relative = entry.get("path")
        expected = entry.get("grimchain")
        size = entry.get("bytes")
        if type(relative) is not str or type(expected) is not str:
            failures.append({"path": relative, "error": "malformed provenance entry"})
            continue
        if isinstance(size, bool) or not isinstance(size, int) or size < 0:
            failures.append({"path": relative, "error": "malformed byte count"})
            continue
        path = ROOT / relative
        checked += 1
        if not path.is_file():
            failures.append({"path": relative, "error": "missing"})
        elif path.stat().st_size != size:
            failures.append({"path": relative, "error": "byte count mismatch"})
        elif not verify_living_domus_value(expected, path, kind="file"):
            failures.append({"path": relative, "error": "Grimchain provenance mismatch"})
    return {
        "name": "release Grimchain provenance",
        "pass": not failures and checked == manifest.get("files"),
        "checked": checked,
        "failures": failures,
    }



def verify_license_metadata() -> dict:
    license_path = ROOT / "LICENSE"
    wheels = sorted((ROOT / "dist").glob(f"tardisha-{VERSION}-*.whl"))
    archives = sorted((ROOT / "dist").glob(f"tardisha-{VERSION}.tar.gz"))
    failures = []
    if not license_path.exists():
        return {"name": "MPL-2.0 license closure", "pass": False, "failures": [{"error": "root LICENSE missing"}]}
    license_bytes = license_path.read_bytes()
    if not license_bytes.startswith(b"Mozilla Public License Version 2.0"):
        failures.append({"error": "root LICENSE is not MPL 2.0 text"})
    if len(wheels) != 1:
        failures.append({"error": f"expected one wheel, found {len(wheels)}"})
    else:
        with zipfile.ZipFile(wheels[0]) as handle:
            names = handle.namelist()
            metadata_name = next((name for name in names if name.endswith(".dist-info/METADATA")), None)
            license_name = next((name for name in names if ".dist-info/licenses/" in name and name.endswith("LICENSE")), None)
            if metadata_name is None:
                failures.append({"error": "wheel METADATA missing"})
            else:
                metadata = handle.read(metadata_name).decode("utf-8", "replace")
                if "License-Expression: MPL-2.0" not in metadata:
                    failures.append({"error": "wheel MPL-2.0 expression missing"})
            if license_name is None:
                failures.append({"error": "wheel LICENSE missing"})
            elif handle.read(license_name) != license_bytes:
                failures.append({"error": "wheel LICENSE bytes differ"})
    if len(archives) != 1:
        failures.append({"error": f"expected one source archive, found {len(archives)}"})
    else:
        with tarfile.open(archives[0], "r:gz") as handle:
            member = next((item for item in handle.getmembers() if item.name.endswith("/LICENSE")), None)
            if member is None:
                failures.append({"error": "source archive LICENSE missing"})
            else:
                extracted = handle.extractfile(member)
                archive_bytes = extracted.read() if extracted is not None else b""
                if archive_bytes != license_bytes:
                    failures.append({"error": "source archive LICENSE bytes differ"})
    manifest_path = ROOT / "SOURCE_GRIMCHAIN_MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    license_entry = next((entry for entry in manifest["entries"] if entry["path"] == "LICENSE"), None)
    if license_entry is None:
        failures.append({"error": "SOURCE_GRIMCHAIN_MANIFEST LICENSE entry missing"})
    elif not verify_living_domus_value(license_entry["grimchain"], license_path, kind="file"):
        failures.append({"error": "SOURCE_GRIMCHAIN_MANIFEST LICENSE provenance differs"})
    return {
        "name": "MPL-2.0 license closure",
        "pass": not failures,
        "license_grimchain": grimchain_provenance(license_path),
        "failures": failures,
    }

def wheel_test() -> dict:
    wheels = sorted((ROOT / "dist").glob(f"tardisha-{VERSION}-*.whl"))
    if len(wheels) != 1:
        return {"name": "installed wheel fixed point", "pass": False, "error": f"expected one wheel, found {len(wheels)}"}
    wheel = wheels[0]
    with tempfile.TemporaryDirectory() as td:
        directory = Path(td)
        venv = directory / "venv"
        subprocess.run([sys.executable, "-m", "venv", str(venv)], check=True, capture_output=True, text=True)
        python = venv / "bin" / "python"
        pip = venv / "bin" / "pip"
        grimchain = venv / "bin" / "grimchain"
        environment = {key: value for key, value in os.environ.items() if key != "PYTHONPATH"}
        install = subprocess.run([str(pip), "install", "--no-deps", str(wheel)], cwd=directory, capture_output=True, text=True, env=environment)
        if install.returncode != 0:
            return {"name": "installed wheel fixed point", "pass": False, "install_stdout": install.stdout, "install_stderr": install.stderr}

        source = directory / "source.txt"
        initial = b"The installed wheel returns through the same path.\n"
        source.write_bytes(initial)
        first = subprocess.run([str(grimchain), str(source)], cwd=directory, check=True, capture_output=True, text=True, env=environment).stdout.rstrip("\n")
        source.write_bytes(initial + first.encode("utf-8") + b"\n")
        second = subprocess.run([str(grimchain), str(source)], cwd=directory, check=True, capture_output=True, text=True, env=environment).stdout.rstrip("\n")
        package_probe = subprocess.run(
            [str(python), "-c", "import TardiSHA; print(TardiSHA.__file__); print(TardiSHA.COMPILED_KERNEL_ACTIVE)"],
            cwd=directory, check=True, capture_output=True, text=True, env=environment,
        ).stdout.splitlines()
        package_path = package_probe[0].strip()
        kernel_active = len(package_probe) > 1 and package_probe[1].strip() == "True"
        return {"name": "installed wheel fixed point", "pass": first == second and "site-packages" in package_path and kernel_active, "wheel": wheel.name, "wheel_grimchain": grimchain_provenance(wheel), "package_path": package_path, "compiled_kernel_active": kernel_active, "first": first, "second": second}



def source_archive_test() -> dict:
    archives = sorted((ROOT / "dist").glob(f"tardisha-{VERSION}.tar.gz"))
    if len(archives) != 1:
        return {"name": "source archive execution", "pass": False, "error": f"expected one source archive, found {len(archives)}"}
    archive = archives[0]
    with tempfile.TemporaryDirectory() as td:
        directory = Path(td)
        with tarfile.open(archive, "r:gz") as handle:
            handle.extractall(directory, filter="data")
        source_root = directory / f"tardisha-{VERSION}"
        manifest_path = source_root / "SOURCE_GRIMCHAIN_MANIFEST.json"
        if not manifest_path.exists():
            return {"name": "source archive execution", "pass": False, "error": "SOURCE_GRIMCHAIN_MANIFEST.json missing"}
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        failures = []
        for entry in manifest["entries"]:
            path = source_root / entry["path"]
            if not path.exists():
                failures.append({"path": entry["path"], "error": "missing"})
            elif path.stat().st_size != entry["bytes"]:
                failures.append({"path": entry["path"], "error": "byte count mismatch"})
            elif not verify_living_domus_value(entry["grimchain"], path, kind="file"):
                failures.append({"path": entry["path"], "error": "Grimchain provenance mismatch"})
        environment = {key: value for key, value in os.environ.items() if key != "PYTHONPATH"}
        build = subprocess.run(
            [sys.executable, "setup.py", "build_ext", "--inplace"],
            cwd=source_root, capture_output=True, text=True, env=environment,
        )
        environment["PYTHONPATH"] = str(source_root)
        selftest = subprocess.run(
            [sys.executable, "TardiSHA_selftest.py"], cwd=source_root,
            capture_output=True, text=True, env=environment,
        ) if build.returncode == 0 else subprocess.CompletedProcess([], 1, "", "source build failed")
        sample = directory / "source.txt"
        initial = b"The source archive carries the same return.\n"
        sample.write_bytes(initial)
        command = source_root / "grimchain"
        first_process = subprocess.run([str(command), str(sample)], cwd=source_root, capture_output=True, text=True, env=environment)
        first = first_process.stdout.rstrip("\n")
        sample.write_bytes(initial + first.encode("utf-8") + b"\n")
        second_process = subprocess.run([str(command), str(sample)], cwd=source_root, capture_output=True, text=True, env=environment)
        second = second_process.stdout.rstrip("\n")
        passed = (
            not failures
            and build.returncode == 0
            and selftest.returncode == 0
            and first_process.returncode == 0
            and second_process.returncode == 0
            and first == second
        )
        return {
            "name": "source archive execution",
            "pass": passed,
            "archive": archive.name,
            "archive_grimchain": grimchain_provenance(archive),
            "manifest_files": manifest["files"],
            "manifest_failures": failures,
            "source_build_returncode": build.returncode,
            "source_build_stdout": build.stdout,
            "source_build_stderr": build.stderr,
            "selftest": selftest.stdout.strip(),
            "selftest_stderr": selftest.stderr,
            "fixed_point": first == second,
        }

def debian_package_test() -> dict:
    packages = sorted((ROOT / "dist").glob(f"tardisha_{VERSION}-1_*.deb"))
    if len(packages) != 1:
        return {"name": "direct Debian package", "pass": False, "error": f"expected one Debian package, found {len(packages)}"}
    package = packages[0]
    architecture = subprocess.run(
        ["dpkg-deb", "-f", str(package), "Architecture"],
        capture_output=True, text=True,
    )
    listing = subprocess.run(
        ["dpkg-deb", "-c", str(package)],
        capture_output=True, text=True,
    )
    required = (
        "/usr/bin/grimchain",
        "/usr/bin/tardisha",
        "/usr/bin/TardiSHA",
        f"/usr/share/tardisha/wheels/tardisha-{VERSION}-cp312-cp312-linux_x86_64.whl",
    )
    passed = (
        architecture.returncode == 0
        and architecture.stdout.strip() == "amd64"
        and listing.returncode == 0
        and all(item in listing.stdout for item in required)
    )
    return {
        "name": "direct Debian package",
        "pass": passed,
        "package": package.name,
        "grimchain": grimchain_provenance(package),
        "architecture": architecture.stdout.strip(),
        "required_paths_present": all(item in listing.stdout for item in required),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--full", action="store_true", help="run the full hostile population and 2000-source independent cross-check")
    args = parser.parse_args()

    environment = {**os.environ, "PYTHONPATH": str(ROOT)}
    decimal_sources = 2000 if args.full else 200
    hostile_sources = 256 if args.full else 32
    lineage = 128 if args.full else 16

    checks = [
        run("built-in self-test", [sys.executable, "TardiSHA_selftest.py"], env=environment),
        run("application integration", [sys.executable, "validation/integration_test.py"], env=environment),
        run("independent Decimal cross-check", [sys.executable, "validation/independent_decimal_crosscheck.py", "--sources", str(decimal_sources)], env=environment),
        run("hostile Aeternum audit", [sys.executable, "validation/hostile_aeternum.py", "--sources", str(hostile_sources), "--lineage", str(lineage)], env=environment),
        run("ALQC Compliance Audit acceptance", [sys.executable, "validation/compliance_audit_test.py"], env=environment),
        verify_provenance_manifest(),
        verify_license_metadata(),
        wheel_test(),
        source_archive_test(),
        debian_package_test(),
    ]

    report = {"suite": f"TardiSHA {VERSION} public release validation", "mode": "full" if args.full else "quick", "passed": sum(bool(item.get("pass")) for item in checks), "failed": sum(not bool(item.get("pass")) for item in checks), "checks": checks}
    target = RESULTS / "release_validation.json"
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"suite": report["suite"], "mode": report["mode"], "passed": report["passed"], "failed": report["failed"], "checks": [{"name": item["name"], "pass": item.get("pass")} for item in checks]}, ensure_ascii=False, indent=2))
    return 0 if report["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
