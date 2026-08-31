#!/usr/bin/env python3
"""Independently validate the Step-6 PySCF basis-resolution index."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

import yaml

from build_basis_bridge import molecular_dimensions
from pyscf_basis_bridge import QCHEM_AUXILIARY_FILES, build_molecules, canonical_hash, resolve_record


ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "revwb97m2"
POLICY_PATH = PROJECT / "manifests/basis_bridge/step6_basis_bridge_v1.yaml"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    policy = yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8"))
    source_root = Path(policy["source_snapshot"]["root"])
    source_path = source_root / policy["source_snapshot"]["records"]
    output_path = ROOT / policy["outputs"]["records"]
    provenance_path = ROOT / policy["outputs"]["provenance"]
    validation_path = ROOT / policy["outputs"]["validation"]
    records = [json.loads(line) for line in source_path.read_text(encoding="utf-8").splitlines()]
    rows = read_csv(output_path)
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    checks: dict[str, bool] = {}
    details: dict[str, object] = {}

    checks["source_snapshot_hashes"] = (
        sha256(source_root / "MANIFEST.sha256") == policy["source_snapshot"]["checksum_manifest_sha256"]
        and sha256(source_path) == policy["source_snapshot"]["records_sha256"]
    )
    checks["record_count_sorted_unique_17658"] = (
        len(records) == len(rows) == 17658
        and [row["species"] for row in rows] == sorted(row["species"] for row in rows)
        and len({row["species"] for row in rows}) == 17658
    )
    checks["qchem_auxiliary_sources_hash_pinned"] = all(
        sha256(QCHEM_AUXILIARY_FILES[name]) == metadata["sha256"]
        for name, metadata in policy["translation"]["qchem_auxiliary_library"]["files"].items()
    )

    counters = {key: Counter() for key in ("orbital_resolution", "auxiliary_resolution", "ecp_resolution", "scope")}
    all_rows_match = True
    positive_dimensions = True
    parity_valid = True
    source_by_species = {record["identity"]["species"]: record for record in records}
    row_by_species = {row["species"]: row for row in rows}
    definition_cache: dict[tuple[object, ...], tuple[dict[str, object], str, str, str]] = {}
    for row in rows:
        record = source_by_species[row["species"]]
        try:
            mol = record["pyscf_molecule"]
            definition_key = (
                record["orbital_basis"]["embedded_block"]["sha256"],
                record["orbital_basis"]["qchem_rem_label"],
                record["auxiliary_basis"]["embedded_block"]["sha256"],
                record["auxiliary_basis"]["qchem_rem_label"],
                record["ecp"]["embedded_block"]["sha256"],
                tuple(mol["elements"]),
                record["identity"]["scope"],
            )
            if definition_key not in definition_cache:
                resolved = resolve_record(record)
                definition_cache[definition_key] = (
                    resolved,
                    canonical_hash(resolved["orbital_basis"]),
                    canonical_hash(resolved["auxiliary_basis"]),
                    canonical_hash(resolved["ecp"]),
                )
            resolved, orbital_hash, auxiliary_hash, ecp_hash = definition_cache[definition_key]
            orbital_dims = molecular_dimensions(mol["atom"], mol["charge"], resolved["orbital_basis"], resolved["ecp"])
            auxiliary_dims = molecular_dimensions(mol["atom"], mol["charge"], resolved["auxiliary_basis"], {})
            expected = {
                "source_record_sha256": record["record_sha256"],
                "qchem_source_input_sha256": record["provenance"]["qchem_source_input_sha256"],
                "orbital_resolution": resolved["orbital_resolution"],
                "orbital_definition_sha256": orbital_hash,
                "auxiliary_resolution": resolved["auxiliary_resolution"],
                "auxiliary_definition_sha256": auxiliary_hash,
                "ecp_resolution": resolved["ecp_resolution"],
                "ecp_definition_sha256": ecp_hash,
                "electron_count": str(orbital_dims["electrons"]),
                "ecp_electrons": str(orbital_dims["ecp_electrons"]),
                "orbital_shells": str(orbital_dims["nbas"]),
                "orbital_spherical_aos": str(orbital_dims["nao"]),
                "auxiliary_shells": str(auxiliary_dims["nbas"]),
                "auxiliary_spherical_aos": str(auxiliary_dims["nao"]),
                "runnable_status": "runnable_basis_metadata_validated",
            }
            all_rows_match = all_rows_match and all(row[key] == value for key, value in expected.items())
            positive_dimensions = positive_dimensions and all(
                int(row[key]) > 0
                for key in ("orbital_shells", "orbital_spherical_aos", "auxiliary_shells", "auxiliary_spherical_aos")
            )
            parity_valid = parity_valid and (int(row["electron_count"]) - int(row["spin"])) % 2 == 0
        except Exception:
            all_rows_match = False
        for key in counters:
            counters[key][row[key]] += 1

    checks["every_resolution_recomputed_from_immutable_record"] = all_rows_match
    checks["all_dimensions_positive"] = positive_dimensions
    checks["electron_spin_parity_valid"] = parity_valid
    checks["translation_counts_exact"] = (
        counters["orbital_resolution"] == Counter({"named_alias": 17065, "embedded_qchem_block": 593})
        and counters["auxiliary_resolution"] == Counter({
            "hash_pinned_qchem_named_library": 14005,
            "explicit_scope_policy": 3652,
            "embedded_qchem_block": 1,
        })
        and counters["ecp_resolution"] == Counter({
            "not_applicable": 17194,
            "implicit_named_def2_ecp": 367,
            "embedded_qchem_block": 97,
        })
    )
    checks["missing_auxiliary_policy_counts_exact"] = (
        counters["scope"]["BigNC_external"] == 75
        and counters["scope"]["GDB9_W1_F12_external"] == 3371
        and counters["scope"]["OPT_external"] == 206
        and sum(counters["scope"].values()) == 17658
    )

    representative_species = [
        "h2o_SW49", "AE11_Yb", "3d4dIPSS_Ag_GS", "3BHET_1.1_dimAB",
        "L14_2a_monA", "dsgdb9nsd_000018", "DAPD_Pd",
    ]
    representative_results: dict[str, object] = {}
    representatives_ok = True
    for species in representative_species:
        if species not in source_by_species:
            representative_results[species] = "missing"
            representatives_ok = False
            continue
        record = source_by_species[species]
        row = row_by_species[species]
        try:
            mol, auxmol, _ = build_molecules(record)
            observed = {
                "electrons": mol.nelectron,
                "orbital_shells": mol.nbas,
                "orbital_spherical_aos": mol.nao_nr(),
                "auxiliary_shells": auxmol.nbas,
                "auxiliary_spherical_aos": auxmol.nao_nr(),
            }
            expected = {
                "electrons": int(row["electron_count"]),
                "orbital_shells": int(row["orbital_shells"]),
                "orbital_spherical_aos": int(row["orbital_spherical_aos"]),
                "auxiliary_shells": int(row["auxiliary_shells"]),
                "auxiliary_spherical_aos": int(row["auxiliary_spherical_aos"]),
            }
            representative_results[species] = observed
            representatives_ok = representatives_ok and observed == expected
        except Exception as exc:
            representative_results[species] = f"{type(exc).__name__}: {exc}"
            representatives_ok = False
    checks["representative_pyscf_molecules_build"] = representatives_ok

    yb = policy["ae11_yb_exception"]
    yb_input = Path(yb["source_input"])
    yb_output = Path(yb["source_output"])
    yb_job = Path(yb["source_job_script"])
    yb_row = row_by_species["AE11_Yb"]
    expected_yb = yb["expected"]
    checks["ae11_yb_prior_evidence_hashes"] = (
        sha256(yb_input) == yb["source_input_sha256"]
        and sha256(yb_output) == yb["source_output_sha256"]
        and sha256(yb_job) == yb["source_job_script_sha256"]
    )
    output_text = yb_output.read_text(encoding="utf-8", errors="replace")
    checks["ae11_yb_qchem_job_completed"] = (
        "Thank you very much for using Q-Chem" in output_text
        and "There are       35 alpha and       35 beta electrons" in output_text
    )
    checks["ae11_yb_exact_dimensions"] = (
        int(yb_row["electron_count"]) == expected_yb["electrons"] == 70
        and int(yb_row["ecp_electrons"]) == expected_yb["ecp_electrons"] == 0
        and int(yb_row["orbital_shells"]) == expected_yb["orbital_shells"] == 50
        and int(yb_row["orbital_spherical_aos"]) == expected_yb["orbital_spherical_aos"] == 184
        and int(yb_row["auxiliary_shells"]) == expected_yb["auxiliary_shells"] == 65
        and int(yb_row["auxiliary_spherical_aos"]) == expected_yb["auxiliary_spherical_aos"] == 285
        and yb_row["orbital_resolution"] == yb_row["auxiliary_resolution"] == "embedded_qchem_block"
        and yb_row["ecp_resolution"] == "not_applicable"
    )
    qchem_regressions_ok = True
    qchem_regression_details: dict[str, object] = {}
    for species, expected in policy["qchem_structural_regressions"].items():
        if species == "contraction_note":
            continue
        output = Path(expected["output"])
        text = output.read_text(encoding="utf-8", errors="replace")
        row = row_by_species[species]
        expected_electrons = expected["electrons"]
        alpha = (expected_electrons + int(row["spin"])) // 2
        beta = expected_electrons - alpha
        observed = {
            "output_hash": sha256(output),
            "electron_count": int(row["electron_count"]),
            "pyscf_orbital_shells": int(row["orbital_shells"]),
            "orbital_spherical_aos": int(row["orbital_spherical_aos"]),
            "pyscf_auxiliary_shells": int(row["auxiliary_shells"]),
            "auxiliary_spherical_aos": int(row["auxiliary_spherical_aos"]),
        }
        case_ok = (
            observed["output_hash"] == expected["output_sha256"]
            and observed["electron_count"] == expected_electrons
            and observed["pyscf_orbital_shells"] == expected["pyscf_orbital_shells"]
            and observed["orbital_spherical_aos"] == expected["orbital_spherical_aos"]
            and observed["pyscf_auxiliary_shells"] == expected["pyscf_auxiliary_shells"]
            and observed["auxiliary_spherical_aos"] == expected["auxiliary_spherical_aos"]
            and f"There are {alpha:8d} alpha and {beta:8d} beta electrons" in text
            and f"There are {expected['qchem_orbital_shells']} shells and {expected['orbital_spherical_aos']} basis functions" in text
            and f"There are {expected['qchem_auxiliary_shells']} shells and {expected['auxiliary_spherical_aos']} basis functions" in text
            and "Thank you very much for using Q-Chem" in text
        )
        observed["passed"] = case_ok
        qchem_regression_details[species] = observed
        qchem_regressions_ok = qchem_regressions_ok and case_ok
    checks["qchem_structural_regressions_match"] = qchem_regressions_ok
    checks["no_qchem_orbitals_or_qarchive"] = (
        provenance["qchem_orbitals_used"] is False and provenance["qarchive_used"] is False
    )
    checks["output_hash_matches_provenance"] = (
        provenance["outputs"][output_path.name]["sha256"] == sha256(output_path)
    )

    details["counters"] = {key: dict(value) for key, value in counters.items()}
    details["representative_results"] = representative_results
    details["qchem_structural_regressions"] = qchem_regression_details
    details["ae11_yb"] = {key: yb_row[key] for key in (
        "electron_count", "ecp_electrons", "orbital_shells", "orbital_spherical_aos",
        "auxiliary_shells", "auxiliary_spherical_aos", "orbital_resolution",
        "auxiliary_resolution", "ecp_resolution",
    )}
    report = {
        "schema_version": 1,
        "status": "passed" if all(checks.values()) else "failed",
        "validator": str(Path(__file__).relative_to(ROOT)),
        "validator_sha256": sha256(Path(__file__)),
        "checks": checks,
        "details": details,
    }
    validation_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
