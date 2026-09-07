#!/usr/bin/env python3
"""Recover a failed Q6 pilot without overwriting any original attempt artifact."""

from __future__ import annotations

import argparse
import json
import os
import re
import resource
import shutil
import subprocess
import sys
import time
import traceback
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from revwb97m2.qchem_feature_publisher import (  # noqa: E402
    publish_or_resume,
    sha256,
)
from revwb97m2.scripts.prepare_q3_qchem_gateway import (  # noqa: E402
    derive_input,
    tree_manifest,
)
from revwb97m2.scripts.run_q6_resource_pilot import (  # noqa: E402
    DEFAULT_MANIFEST,
    DEFAULT_RUN_ROOT,
    QCAUX,
    QCHEM_ROOT,
    RETRY_CONTROL_AMENDMENT,
    canonical_tree_hash,
    child_max_rss_mb,
    d4_atm,
    directory_bytes,
)


TOTAL_WALL_RE = re.compile(r"Total job time:\s*([0-9]+(?:\.[0-9]+)?)s\(wall\)")


def qchem_reported_wall_seconds(output: Path) -> float:
    matches = TOTAL_WALL_RE.findall(output.read_text(encoding="utf-8", errors="replace"))
    if len(matches) != 1:
        raise ValueError(f"expected one Q-Chem total-wall record in {output}, got {len(matches)}")
    value = float(matches[0])
    if value <= 0:
        raise ValueError(f"non-positive Q-Chem total wall time in {output}")
    return value


def observed_tree(path: Path) -> dict[str, object]:
    records = tree_manifest(path)
    return {
        "records": records,
        "summary": {
            "files": len(records),
            "bytes": sum(int(row["bytes"]) for row in records),
            "manifest_sha256": canonical_tree_hash(records),
        },
    }


def prepare_isolated_copy(source: Path, destination: Path, expected_records: list[dict[str, object]]) -> float:
    started = time.perf_counter()
    shutil.copytree(source, destination, copy_function=shutil.copy2)
    elapsed = time.perf_counter() - started
    if tree_manifest(destination) != expected_records:
        raise ValueError(f"isolated retry copy differs from frozen source: {destination}")
    return elapsed


def run_qchem(case_root: Path, cpus: int) -> tuple[float, float]:
    environment = os.environ.copy()
    environment.update(
        {
            "QC": str(QCHEM_ROOT),
            "QCPROG": str(QCHEM_ROOT / "exe/qcprog.exe"),
            "QCAUX": QCAUX,
            "QCSCRATCH": str(case_root / "qcscratch"),
            "QCHEM_PRINT_INTEGRATED_DV": "1",
        }
    )
    environment.pop("QCLOCALSCR", None)
    environment.pop("QCHEM_DUMP_INTEGRATED_DV_INPUTS", None)
    started = time.perf_counter()
    with (case_root / "qchem.launch.stdout").open("xb") as stdout, (case_root / "qchem.launch.stderr").open("xb") as stderr:
        subprocess.run(
            [
                str(QCHEM_ROOT / "bin/qchem"),
                "-save",
                "-nt",
                str(cpus),
                str(case_root / "input.q3.in"),
                str(case_root / "qchem.out"),
                "q6_gateway",
            ],
            env=environment,
            stdout=stdout,
            stderr=stderr,
            check=True,
        )
    process_wall = time.perf_counter() - started
    return process_wall, qchem_reported_wall_seconds(case_root / "qchem.out")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--species", required=True)
    parser.add_argument("--cpus", required=True, type=int)
    parser.add_argument("--attempt", required=True)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--run-root", type=Path, default=DEFAULT_RUN_ROOT)
    args = parser.parse_args()
    if not re.fullmatch(r"retry[1-9][0-9]*", args.attempt):
        raise ValueError("attempt must be retry1, retry2, ...")

    manifest_path = args.manifest.resolve()
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    matches = [row for row in manifest["cases"] if row["species"] == args.species]
    if manifest["status"] != "frozen_before_results" or len(matches) != 1:
        raise ValueError("Q6 recovery requires one case in the frozen manifest")
    case = matches[0]
    if args.cpus != int(case["resources"]["cpus"]):
        raise ValueError("retry CPU count must match the frozen pilot")

    species_root = args.run_root.resolve() / args.species
    original_failure = species_root / "FAILURE.json"
    if not original_failure.is_file() or (species_root / "Q6_PILOT_COMPLETE").exists():
        raise ValueError("Q6 recovery requires an incomplete pilot with a preserved failure record")
    attempt_root = species_root / "attempts" / args.attempt
    if attempt_root.exists():
        raise FileExistsError(f"refusing to overwrite Q6 retry: {attempt_root}")
    attempt_root.mkdir(parents=True)
    started_total = time.perf_counter()

    try:
        source_root = Path(manifest["authorities"]["orbital_root"]) / args.species
        input_source = Path(manifest["authorities"]["authoritative_input_root"]) / args.species / "input0"
        if sha256(input_source) != case["authoritative_input_sha256"]:
            raise ValueError("Q6 retry authoritative input hash mismatch")
        hash_started = time.perf_counter()
        source = observed_tree(source_root)
        source_hash_seconds = time.perf_counter() - hash_started
        if source["summary"] != case["source_tree"]:
            raise ValueError("Q6 retry authoritative tree differs from frozen manifest")

        retry_stage = attempt_root / "staged_orbitals"
        stage_copy_seconds = prepare_isolated_copy(source_root, retry_stage, source["records"])
        grid_reports = []
        for grid in manifest["grids"]:
            grid_id = str(grid["id"])
            original_case = species_root / "cases" / grid_id
            feature_root = species_root / "features" / grid_id
            if feature_root.exists():
                copy_root = attempt_root / "copy_benchmarks" / grid_id
                copy_seconds = prepare_isolated_copy(retry_stage, copy_root, source["records"])
                publication_benchmark = attempt_root / "publication_benchmarks" / grid_id
                extraction_started = time.perf_counter()
                benchmark_action, _ = publish_or_resume(original_case, publication_benchmark)
                extraction_seconds = time.perf_counter() - extraction_started
                if benchmark_action != "published":
                    raise RuntimeError(f"grid {grid_id} extraction benchmark was not freshly published")
                restart_started = time.perf_counter()
                action, feature_manifest = publish_or_resume(original_case, feature_root)
                restart_seconds = time.perf_counter() - restart_started
                if action != "reused":
                    raise RuntimeError(f"existing grid {grid_id} was not independently reusable")
                qchem_output = original_case / "qchem.out"
                grid_reports.append(
                    {
                        "grid": grid_id,
                        "execution_origin": "original_successful_attempt",
                        "case_root": str(original_case),
                        "isolated_copy_seconds": copy_seconds,
                        "isolated_copy_measurement": "repeated_during_recovery",
                        "isolated_copy_bytes": case["source_tree"]["bytes"],
                        "qchem_wall_seconds": qchem_reported_wall_seconds(qchem_output),
                        "qchem_wall_measurement": "qchem_total_job_time",
                        "qchem_output_bytes": qchem_output.stat().st_size,
                        "extraction_publication_seconds": extraction_seconds,
                        "extraction_measurement": "repeated_to_attempt_scoped_boundary",
                        "restart_revalidation_seconds": restart_seconds,
                        "complete_block_count": feature_manifest["complete_block_count"],
                        "feature_artifact_bytes": directory_bytes(feature_root),
                        "feature_manifest_sha256": sha256(feature_root / "qchem_integrated_dv_manifest.json"),
                        "child_max_rss_mb_after_grid": None,
                    }
                )
                continue

            retry_case = attempt_root / "cases" / grid_id
            scratch_root = retry_case / "qcscratch" / "q6_gateway"
            retry_case.mkdir(parents=True)
            shutil.copy2(input_source, retry_case / "input.authoritative.in")
            (retry_case / "input.q3.in").write_text(
                derive_input(
                    input_source.read_text(encoding="utf-8"),
                    str(grid["qchem_value"]),
                    skip_post_fock_diagonalization=True,
                ),
                encoding="utf-8",
            )
            copy_seconds = prepare_isolated_copy(retry_stage, scratch_root, source["records"])
            prepared = {
                "species": args.species,
                "role": case["size_role"],
                "grid": grid_id,
                "case_root": str(retry_case.resolve()),
                "source_orbital_root": str(source_root.resolve()),
                "source_tree": source["records"],
                "copy_tree": tree_manifest(scratch_root),
                "source_copy_tree_identity": True,
                "authoritative_input_sha256": sha256(input_source),
                "derived_input_sha256": sha256(retry_case / "input.q3.in"),
                "recovery_attempt": args.attempt,
                "original_failure_sha256": sha256(original_failure),
                "mp2_restart_no_scf_required": True,
                "q6_control_amendment": str(RETRY_CONTROL_AMENDMENT),
                "q6_control_amendment_sha256": sha256(RETRY_CONTROL_AMENDMENT),
            }
            (retry_case / "PREPARED.json").write_text(
                json.dumps(prepared, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
            process_wall, reported_wall = run_qchem(retry_case, args.cpus)
            extraction_started = time.perf_counter()
            action, feature_manifest = publish_or_resume(retry_case, feature_root)
            extraction_seconds = time.perf_counter() - extraction_started
            if action != "published":
                raise RuntimeError("missing retry feature boundary was not freshly published")
            restart_started = time.perf_counter()
            restart_action, _ = publish_or_resume(retry_case, feature_root)
            restart_seconds = time.perf_counter() - restart_started
            if restart_action != "reused":
                raise RuntimeError("retry feature boundary failed immediate restart validation")
            report = {
                "grid": grid_id,
                "execution_origin": args.attempt,
                "case_root": str(retry_case),
                "isolated_copy_seconds": copy_seconds,
                "isolated_copy_measurement": "retry_execution_copy",
                "isolated_copy_bytes": case["source_tree"]["bytes"],
                "qchem_wall_seconds": reported_wall,
                "qchem_process_wall_seconds": process_wall,
                "qchem_wall_measurement": "qchem_total_job_time",
                "qchem_output_bytes": (retry_case / "qchem.out").stat().st_size,
                "extraction_publication_seconds": extraction_seconds,
                "restart_revalidation_seconds": restart_seconds,
                "complete_block_count": feature_manifest["complete_block_count"],
                "feature_artifact_bytes": directory_bytes(feature_root),
                "feature_manifest_sha256": sha256(feature_root / "qchem_integrated_dv_manifest.json"),
                "child_max_rss_mb_after_grid": child_max_rss_mb(),
            }
            grid_reports.append(report)
            (attempt_root / f"grid_{grid_id}_measurement.json").write_text(
                json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )

        d4_started = time.perf_counter()
        d4_energy, atom_count = d4_atm(args.species, case["source_record_sha256"])
        d4_seconds = time.perf_counter() - d4_started
        d4_payload = {
            "definition": "pure_three_body_coach_d4_atm",
            "damping_parameters": {
                "s6": 0.0, "s8": 0.0, "s9": 1.0, "a1": 0.215, "a2": 5.8, "alp": 16.0
            },
            "energy_hartree": d4_energy,
            "atom_count": atom_count,
            "wall_seconds": d4_seconds,
            "source_record_sha256": case["source_record_sha256"],
        }
        d4_root = species_root / "d4_atm"
        if d4_root.exists():
            raise FileExistsError(f"refusing to overwrite D4 boundary: {d4_root}")
        d4_root.mkdir()
        (d4_root / "d4_atm.json").write_text(
            json.dumps(d4_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        summary = {
            "schema_version": 1,
            "status": "q6_resource_pilot_complete_and_validated_after_retry",
            "species": args.species,
            "size_role": case["size_role"],
            "manifest": str(manifest_path),
            "manifest_sha256": sha256(manifest_path),
            "resources": case["resources"],
            "attempt_history": {
                "original_failure": str(original_failure),
                "original_failure_sha256": sha256(original_failure),
                "successful_recovery": str(attempt_root),
                "successful_recovery_label": args.attempt,
                "q6_control_amendment": str(RETRY_CONTROL_AMENDMENT),
                "q6_control_amendment_sha256": sha256(RETRY_CONTROL_AMENDMENT),
            },
            "measurements": {
                "authoritative_tree_hash_seconds": source_hash_seconds,
                "source_to_stage_copy_seconds": stage_copy_seconds,
                "source_tree": source["summary"],
                "grid_reports": grid_reports,
                "d4_atm": d4_payload,
                "total_wall_seconds": time.perf_counter() - started_total,
                "child_max_rss_mb": child_max_rss_mb(),
            },
        }
        (species_root / "summary.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        (species_root / "Q6_PILOT_COMPLETE").write_text("complete_after_retry\n", encoding="utf-8")
        summary["measurements"]["total_retained_bytes"] = directory_bytes(species_root)
        (species_root / "summary.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except BaseException:
        (attempt_root / "FAILURE.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "status": "q6_resource_pilot_recovery_failed",
                    "species": args.species,
                    "attempt": args.attempt,
                    "exception": traceback.format_exc(),
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        raise


if __name__ == "__main__":
    raise SystemExit(main())
