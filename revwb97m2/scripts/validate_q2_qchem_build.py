#!/usr/bin/env python3
"""Validate the pinned Q2 Q-Chem build after its Slurm job finishes."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
from pathlib import Path

import yaml


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_key_values(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for line in path.read_text(encoding="utf-8").splitlines():
        key, separator, value = line.partition("=")
        if separator:
            values[key] = value
    return values


def command_output(*args: str) -> str:
    return subprocess.check_output(args, text=True).strip()


def validate_runtime_probe(probe: dict) -> tuple[dict[str, bool], dict]:
    """Recheck the retained lightweight record and, when present, its /tmp files."""
    expected = probe["expected"]
    observed = probe["observed"]
    checks = {
        "probe_archive_read": observed["mo_coefficient_read_messages"] >= 2,
        "probe_one_complete_block": (
            observed["begin_markers"] == observed["end_markers"] == 1
        ),
        "probe_matrix_shape": (
            observed["rows"] == expected["rows"]
            and observed["columns"] == expected["columns"]
        ),
        "probe_numeric_finite": (
            observed["nonnumeric_values"] == 0
            and observed["nonfinite_values"] == 0
        ),
        "probe_normal_termination": observed["normal_qchem_termination"] is True,
    }
    details = {"recorded": observed, "live_files_checked": False}
    input_path = Path(probe["input"]["path"])
    output_path = Path(probe["output"]["path"])
    if input_path.is_file() and output_path.is_file():
        text = output_path.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()
        begin = [i for i, line in enumerate(lines) if "COACH integratedDV begin" in line]
        end = [i for i, line in enumerate(lines) if "COACH integratedDV end" in line]
        rows: list[list[float]] = []
        label_ok = False
        if len(begin) == len(end) == 1 and begin[0] < end[0]:
            block = lines[begin[0] + 1 : end[0]]
            label_ok = bool(block) and block[0].strip() == "integratedDV"
            try:
                rows = [[float(value) for value in line.split()] for line in block[1:]]
            except ValueError:
                rows = []
        live = {
            "input_sha256": sha256(input_path),
            "output_sha256": sha256(output_path),
            "begin_markers": len(begin),
            "end_markers": len(end),
            "label_ok": label_ok,
            "rows": len(rows),
            "columns": len(rows[0]) if rows else 0,
            "all_rows_same_width": bool(rows) and all(len(row) == len(rows[0]) for row in rows),
            "all_values_finite": bool(rows) and all(math.isfinite(value) for row in rows for value in row),
            "mo_coefficient_read_messages": text.count("Reading MOs from coefficient file"),
            "normal_qchem_termination": "Thank you very much for using Q-Chem" in text,
        }
        checks["live_probe_hashes_match"] = (
            live["input_sha256"] == probe["input"]["sha256"]
            and live["output_sha256"] == probe["output"]["sha256"]
        )
        checks["live_probe_contract_matches"] = (
            live["begin_markers"] == live["end_markers"] == 1
            and live["label_ok"]
            and live["rows"] == expected["rows"]
            and live["columns"] == expected["columns"]
            and live["all_rows_same_width"]
            and live["all_values_finite"]
            and live["mo_coefficient_read_messages"] >= 2
            and live["normal_qchem_termination"]
        )
        details = {"recorded": observed, "live_files_checked": True, "live": live}
    return checks, details


def validate_v2(manifest: dict, manifest_path: Path) -> dict:
    source = manifest["source"]
    build = manifest["build"]
    executable = Path(build["executable"])
    libks = Path(build["installed_libks"])
    probe_path = Path(manifest_path.parent / manifest["runtime_probe_record"])
    checks: dict[str, bool] = {
        "manifest_complete": manifest["status"] == "complete",
        "executable_regular_nonempty": executable.is_file() and executable.stat().st_size > 0,
        "executable_hash_matches": executable.is_file() and sha256(executable) == build["executable_sha256"],
        "installed_libks_hash_matches": libks.is_file() and sha256(libks) == build["installed_libks_sha256"],
        "runtime_probe_record_exists": probe_path.is_file(),
    }
    current_source_checks: dict[str, bool] = {}
    try:
        current_source_checks["qchem_revision"] = (
            command_output("svn", "info", "--show-item", "revision", source["qchem_root"])
            == str(source["qchem_svn_revision"])
        )
        current_source_checks["libks_revision"] = (
            command_output("svn", "info", "--show-item", "revision", source["libks_root"])
            == str(source["libks_svn_revision"])
        )
        diff = subprocess.check_output(["svn", "diff", source["libks_root"]])
        current_source_checks["libks_diff"] = hashlib.sha256(diff).hexdigest() == source["libks_local_diff_sha256"]
        for record in source["allowed_local_changes"]:
            path = Path(source["qchem_root"]) / record["path"]
            current_source_checks[record["path"]] = path.is_file() and sha256(path) == record["sha256"]
    except (OSError, subprocess.CalledProcessError):
        current_source_checks["inspection_error"] = False
    checks["current_source_matches"] = all(current_source_checks.values())
    try:
        ldd = command_output("ldd", str(executable))
        checks["dynamic_dependencies_resolved"] = "not found" not in ldd
        ldd_entries = len(ldd.splitlines())
    except (OSError, subprocess.CalledProcessError):
        checks["dynamic_dependencies_resolved"] = False
        ldd_entries = 0
    probe_details = None
    if probe_path.is_file():
        probe = json.loads(probe_path.read_text(encoding="utf-8"))
        probe_checks, probe_details = validate_runtime_probe(probe)
        checks.update(probe_checks)
    passed = all(checks.values())
    return {
        "schema_version": 2,
        "status": "passed" if passed else "failed",
        "passed": passed,
        "manifest": str(manifest_path),
        "manifest_sha256": sha256(manifest_path),
        "checks": checks,
        "details": {
            "executable": str(executable),
            "executable_sha256": sha256(executable) if executable.is_file() else None,
            "installed_libks": str(libks),
            "installed_libks_sha256": sha256(libks) if libks.is_file() else None,
            "ldd_entries": ldd_entries,
            "current_source_checks": current_source_checks,
            "runtime_probe": probe_details,
        },
    }


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=project_root / "manifests/qchem_build/q2_qchem_build_v2.yaml",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    manifest = yaml.safe_load(args.manifest.read_text(encoding="utf-8"))
    if manifest.get("schema_version") == 2:
        report = validate_v2(manifest, args.manifest)
        rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8")
        print(rendered, end="")
        return 0 if report["passed"] else 1

    source = manifest["source"]
    build = manifest["build"]
    install_root = Path(build["install_root"])
    executable = install_root / build["expected_executable"]
    provenance_path = install_root / "build_provenance.txt"
    executable_hash_path = install_root / "executable.sha256"
    ldd_path = install_root / "executable.ldd.txt"
    provenance = parse_key_values(provenance_path)

    checks: dict[str, bool] = {}
    checks["manifest_submitted"] = manifest["status"] in {"submitted", "complete"}
    checks["build_complete_marker"] = (install_root / "BUILD_COMPLETE").is_file()
    checks["provenance_exists"] = provenance_path.is_file()
    checks["source_revisions_match"] = (
        provenance.get("qchem_svn_revision") == str(source["qchem_svn_revision"])
        and provenance.get("libks_svn_revision") == str(source["libks_svn_revision"])
        and provenance.get("qchem_svn_url") == source["qchem_svn_url"]
        and provenance.get("libks_svn_url") == source["libks_svn_url"]
    )
    checks["local_diff_matches"] = (
        provenance.get("libks_local_diff_sha256") == source["libks_local_diff_sha256"]
    )
    checks["compiler_recorded"] = all(
        "10.5.0" in provenance.get(key, "") for key in ("cc", "cxx", "fc")
    )
    checks["configure_arguments_match"] = (
        provenance.get("configure_arguments") == "gnu openmp relwdeb version"
    )
    checks["executable_regular_nonempty"] = executable.is_file() and executable.stat().st_size > 0

    recorded_executable_hash = ""
    if executable_hash_path.is_file():
        recorded_executable_hash = executable_hash_path.read_text(encoding="utf-8").split()[0]
    checks["executable_hash_matches"] = (
        executable.is_file()
        and bool(recorded_executable_hash)
        and recorded_executable_hash == sha256(executable)
        and provenance.get("executable_sha256") == recorded_executable_hash
    )
    checks["dynamic_dependencies_recorded"] = ldd_path.is_file()
    checks["dynamic_dependencies_resolved"] = (
        ldd_path.is_file() and "not found" not in ldd_path.read_text(encoding="utf-8")
    )
    checks["configuration_and_build_logs_exist"] = all(
        (install_root / name).is_file() and (install_root / name).stat().st_size > 0
        for name in ("configure.log", "build.log", "install.log")
    )

    current_source_checks: dict[str, bool] = {}
    try:
        current_source_checks["qchem_revision"] = (
            command_output("svn", "info", "--show-item", "revision", source["qchem_root"])
            == str(source["qchem_svn_revision"])
        )
        current_source_checks["libks_revision"] = (
            command_output("svn", "info", "--show-item", "revision", source["libks_root"])
            == str(source["libks_svn_revision"])
        )
        diff = subprocess.check_output(["svn", "diff", source["libks_root"]])
        current_source_checks["libks_diff"] = (
            hashlib.sha256(diff).hexdigest() == source["libks_local_diff_sha256"]
        )
        for record in source["allowed_local_changes"]:
            path = Path(source["qchem_root"]) / record["path"]
            current_source_checks[record["path"]] = path.is_file() and sha256(path) == record["sha256"]
    except (OSError, subprocess.CalledProcessError):
        current_source_checks["inspection_error"] = False
    checks["current_source_still_matches_build_request"] = all(current_source_checks.values())

    report = {
        "schema_version": 1,
        "status": "passed" if all(checks.values()) else "failed",
        "passed": all(checks.values()),
        "manifest": str(args.manifest),
        "manifest_sha256": sha256(args.manifest),
        "checks": checks,
        "details": {
            "install_root": str(install_root),
            "executable": str(executable),
            "executable_sha256": recorded_executable_hash or None,
            "provenance": provenance,
            "current_source_checks": current_source_checks,
        },
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
