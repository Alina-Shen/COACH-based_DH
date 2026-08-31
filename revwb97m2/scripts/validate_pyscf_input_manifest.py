#!/usr/bin/env python3
"""Independently validate and optionally finalize an all-UKS PySCF input snapshot."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "revwb97m2"
POLICY = PROJECT / "manifests/pyscf_inputs/pyscf_input_policy_v2.yaml"
QCHEM_METADATA = PROJECT / "manifests/data_roles/qchem_input_metadata.csv"
SPECIES_ROLES = PROJECT / "manifests/data_roles/species_roles.csv"
ROLE_NAMES = (
    "coefficient_fitting",
    "model_selection",
    "overfitting_diagnostic",
    "final_assessment",
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def qchem_block(text: str, name: str, required: bool = False) -> str:
    match = re.search(
        rf"(?ims)^\s*\${re.escape(name)}\s*$\n(.*?)^\s*\$end\s*$", text
    )
    if match:
        return match.group(1)
    if required:
        raise ValueError(f"missing ${name} block")
    return ""


def parse_molecule(text: str) -> dict[str, object]:
    molecule = qchem_block(text, "molecule", required=True)
    lines = [
        line.strip()
        for line in molecule.splitlines()
        if line.strip() and not line.lstrip().startswith(("!", "#"))
    ]
    charge, multiplicity = map(int, lines[0].split()[:2])
    source_geometry: list[str] = []
    pyscf_geometry: list[str] = []
    real_atoms = 0
    ghost_atoms = 0
    after_separator = False
    for line in lines[1:]:
        if line == "--":
            after_separator = True
            continue
        fields = line.split()
        if after_separator and len(fields) >= 2 and re.fullmatch(r"[+-]?\d+", fields[0]) and fields[1].isdigit():
            after_separator = False
            continue
        after_separator = False
        for coordinate in fields[1:4]:
            float(coordinate)
        match = re.fullmatch(r"(@?)([A-Za-z]{1,3})", fields[0])
        if not match:
            raise ValueError(f"unsupported atom label: {fields[0]}")
        element = match.group(2).capitalize()
        if match.group(1):
            ghost_atoms += 1
            label = f"Ghost-{element}"
        else:
            real_atoms += 1
            label = element
        source_geometry.append(line)
        pyscf_geometry.append(" ".join([label, *fields[1:]]))
    atom = "\n".join(pyscf_geometry)
    return {
        "charge": charge,
        "multiplicity": multiplicity,
        "spin": multiplicity - 1,
        "real_atom_count": real_atoms,
        "ghost_atom_count": ghost_atoms,
        "molecule_block_sha256": sha256_bytes(molecule.encode()),
        "geometry_payload_sha256": sha256_bytes(("\n".join(source_geometry) + "\n").encode()),
        "atom": atom,
        "atom_sha256": sha256_bytes((atom + "\n").encode()),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--finalize", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    snapshot = args.snapshot.resolve()
    policy = yaml.safe_load(POLICY.read_text(encoding="utf-8"))
    records_path = snapshot / policy["output"]["records"]
    index_path = snapshot / policy["output"]["index"]
    provenance_path = snapshot / policy["output"]["provenance"]
    validation_path = snapshot / policy["output"]["validation"]
    checksum_path = snapshot / policy["output"]["checksum_manifest"]
    immutable_path = snapshot / policy["output"]["immutable_marker"]

    checks: dict[str, bool] = {}
    details: dict[str, object] = {}
    metadata = {row["species"]: row for row in read_csv(QCHEM_METADATA)}
    roles = {row["species"]: row for row in read_csv(SPECIES_ROLES)}
    index_rows = read_csv(index_path)
    records = [json.loads(line) for line in records_path.read_text(encoding="utf-8").splitlines()]
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))

    checks["policy_frozen_all_uks_v2"] = (
        policy["status"] == "frozen"
        and policy["pyscf_molecule"]["reference_policy"]["scf_class"] == "UKS"
        and policy["pyscf_molecule"]["reference_policy"]["exceptions_allowed"] is False
    )
    checks["record_index_counts_17658"] = len(records) == len(index_rows) == len(metadata) == 17658
    record_species = [record["identity"]["species"] for record in records]
    checks["records_sorted_and_unique"] = record_species == sorted(record_species) and len(set(record_species)) == 17658
    checks["index_identity_matches_records"] = all(
        int(row["line_number"]) == number
        and row["species"] == record["identity"]["species"]
        and row["record_sha256"] == record["record_sha256"]
        for number, (row, record) in enumerate(zip(index_rows, records, strict=True), 1)
    )

    records_ok = True
    all_uks = True
    role_counts = Counter()
    scope_counts = Counter()
    ghost_species = 0
    ghost_centers = 0
    missing_aux_energy = 0
    generated_orbital = 0
    generated_auxiliary = 0
    generated_ecp = 0
    for row, record in zip(index_rows, records, strict=True):
        species = record["identity"]["species"]
        source_metadata = metadata[species]
        source = Path(record["provenance"]["qchem_source_input"])
        try:
            data = source.read_bytes()
            text = data.decode("utf-8")
            molecule = parse_molecule(text)
            basis_block = qchem_block(text, "basis")
            auxiliary_block = qchem_block(text, "aux_basis")
            ecp_block = qchem_block(text, "ecp")
        except (OSError, UnicodeDecodeError, ValueError):
            records_ok = False
            continue

        payload_record = dict(record)
        observed_record_hash = payload_record.pop("record_sha256")
        payload = json.dumps(payload_record, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        source_role = roles.get(species)
        expected_roles = {
            role: bool(source_role and source_role[role] == "true") for role in ROLE_NAMES
        }
        rec_molecule = record["pyscf_molecule"]
        reference = record["reference"]
        orbital = record["orbital_basis"]
        auxiliary = record["auxiliary_basis"]
        ecp = record["ecp"]
        row_ok = (
            sha256_bytes(data) == source_metadata["input_sha256"] == record["provenance"]["qchem_source_input_sha256"]
            and molecule["charge"] == rec_molecule["charge"] == int(source_metadata["charge"])
            and molecule["multiplicity"] == rec_molecule["multiplicity"] == int(source_metadata["multiplicity"])
            and molecule["spin"] == rec_molecule["spin"] == int(source_metadata["multiplicity"]) - 1
            and molecule["real_atom_count"] == rec_molecule["real_atom_count"] == int(source_metadata["real_atom_count"])
            and molecule["ghost_atom_count"] == rec_molecule["ghost_atom_count"] == int(source_metadata["ghost_atom_count"])
            and molecule["atom"] == rec_molecule["atom"]
            and molecule["atom_sha256"] == rec_molecule["atom_sha256"] == row["pyscf_atom_sha256"]
            and molecule["molecule_block_sha256"] == source_metadata["molecule_block_sha256"]
            and molecule["geometry_payload_sha256"] == source_metadata["geometry_payload_sha256"]
            and record["identity"]["roles"] == expected_roles
            and record["identity"]["required_for_energy_roles"] == any(expected_roles.values())
            and orbital["manifest_label"] == source_metadata["manifest_orbital_basis"]
            and orbital["qchem_rem_label"] == source_metadata["qchem_rem_basis"]
            and orbital["embedded_block"]["qchem_block"] == basis_block
            and auxiliary["manifest_label"] == source_metadata["manifest_auxiliary_basis"]
            and auxiliary["qchem_rem_label"] == source_metadata["qchem_rem_auxiliary_basis"]
            and auxiliary["embedded_block"]["qchem_block"] == auxiliary_block
            and ecp["qchem_rem_label"] == source_metadata["qchem_rem_ecp"]
            and ecp["embedded_block"]["qchem_block"] == ecp_block
            and observed_record_hash == sha256_bytes(payload.encode()) == row["record_sha256"]
            and record["provenance"]["qchem_orbitals_used"] is False
            and record["provenance"]["qarchive_used"] is False
        )
        records_ok = records_ok and row_ok
        all_uks = all_uks and (
            reference["scf_class"] == "UKS"
            and reference["post_scf_mp2_class"] == "UMP2"
            and reference["unrestricted"] is True
            and reference["exceptions_allowed"] is False
            and row["scf_class"] == "UKS"
            and row["post_scf_mp2_class"] == "UMP2"
        )
        for role, enabled in expected_roles.items():
            role_counts[role] += enabled
        scope_counts[record["identity"]["scope"]] += 1
        ghost_species += molecule["ghost_atom_count"] > 0
        ghost_centers += molecule["ghost_atom_count"]
        missing_aux_energy += (
            record["identity"]["required_for_energy_roles"]
            and auxiliary["source_kind"] == "not_specified_in_source"
        )
        generated_orbital += orbital["embedded_block"]["present"]
        generated_auxiliary += auxiliary["embedded_block"]["present"]
        generated_ecp += ecp["embedded_block"]["present"]

    checks["every_record_independently_reparsed_and_rehashed"] = records_ok
    checks["all_17658_inputs_are_uks_and_ump2"] = all_uks
    checks["energy_species_exact_17452"] = sum(
        record["identity"]["required_for_energy_roles"] for record in records
    ) == 17452
    checks["opt_species_exact_206_separate_track"] = sum(
        record["identity"]["scope"] == "OPT_external"
        and record["identity"]["evaluation_track"] == "geometry_optimization"
        for record in records
    ) == 206
    checks["role_counts_exact"] = role_counts == Counter(policy["scope"]["energy_roles"])
    checks["ghost_centers_preserved"] = ghost_species == 50 and ghost_centers == 2771
    checks["basis_bridge_remains_explicitly_pending"] = all(
        record["runnable_status"] == "blocked_pending_step_6_basis_bridge_validation"
        for record in records
    )
    checks["provenance_output_hashes"] = (
        provenance["outputs"][records_path.name]["sha256"] == sha256(records_path)
        and provenance["outputs"][index_path.name]["sha256"] == sha256(index_path)
        and provenance["outputs"]["policy.yaml"]["sha256"] == sha256(snapshot / "policy.yaml")
    )
    checks["no_qchem_orbital_sources"] = provenance["qchem_orbitals_used"] is False

    details.update(
        {
            "scope_counts": dict(scope_counts),
            "role_counts": dict(role_counts),
            "ghost_species": ghost_species,
            "ghost_centers": ghost_centers,
            "energy_species_missing_source_auxiliary_basis": missing_aux_energy,
            "embedded_orbital_basis_blocks": generated_orbital,
            "embedded_auxiliary_basis_blocks": generated_auxiliary,
            "embedded_ecp_blocks": generated_ecp,
        }
    )
    report = {
        "schema_version": 1,
        "status": "passed" if all(checks.values()) else "failed",
        "validator": str(Path(__file__).relative_to(ROOT)),
        "validator_sha256": sha256(Path(__file__)),
        "checks": checks,
        "details": details,
    }
    if args.finalize:
        if validation_path.exists() or checksum_path.exists() or immutable_path.exists():
            raise SystemExit("refusing to overwrite existing finalization artifacts")
        if report["status"] != "passed":
            print(json.dumps(report, indent=2, sort_keys=True))
            return 1
        validation_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        manifest_files = [records_path, index_path, snapshot / "policy.yaml", provenance_path, validation_path]
        checksum_lines = [f"{sha256(path)}  {path.name}" for path in manifest_files]
        checksum_path.write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")
        immutable = {
            "schema_version": 1,
            "status": "immutable_complete",
            "snapshot_name": policy["name"],
            "record_count": len(records),
            "manifest": checksum_path.name,
            "manifest_sha256": sha256(checksum_path),
            "qchem_orbitals_used": False,
            "reference_policy": "UKS_for_all_species",
            "basis_bridge_status": "pending_step_6_semantic_translation_and_validation",
        }
        immutable_path.write_text(json.dumps(immutable, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        report["finalization"] = immutable
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
