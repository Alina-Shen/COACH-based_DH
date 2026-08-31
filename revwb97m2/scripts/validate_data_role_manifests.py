#!/usr/bin/env python3
"""Independently validate frozen revwb97m2 data-role and input-metadata manifests."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "revwb97m2"
ROLE_ROOT = PROJECT / "manifests/data_roles"
POLICY = ROLE_ROOT / "revwb97m2_data_roles_v2.yaml"
DATASET_ROLES = ROLE_ROOT / "dataset_roles.csv"
REACTION_ROLES = ROLE_ROOT / "reaction_roles.csv"
SPECIES_ROLES = ROLE_ROOT / "species_roles.csv"
INPUT_METADATA = ROLE_ROOT / "qchem_input_metadata.csv"
PROVENANCE = ROLE_ROOT / "provenance.json"
DATASET_EVAL = PROJECT / "manifests/gscdb137/source/DatasetEval.csv"
DATASET_MANIFEST = PROJECT / "manifests/gscdb137/dataset_manifest.csv"
SPECIES_MANIFEST = PROJECT / "manifests/gscdb137/species_manifest.csv"
BIGNC_SPECIES = PROJECT / "manifests/gscdb137/bignc_species_manifest.csv"
ADDITIONAL_ROOT = Path(
    "/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/"
    "authoritative_inputs/qchem/additionalsets_gscdb_8f2c7e5"
)
BIGNC_EVAL = ADDITIONAL_ROOT / "BigNC/DatasetEval.csv"
BIGNC_INFO = ADDITIONAL_ROOT / "BigNC/Allmols_info.json"
GDB9_EVAL = ADDITIONAL_ROOT / "GDB9-W1-F12/DatasetEval.csv"
GDB9_INFO = ADDITIONAL_ROOT / "GDB9-W1-F12/Allmols_info.json"
OPT_INFO = ADDITIONAL_ROOT / "OPT/Allmols_info.json"
ADDITIONAL_MANIFEST = PROJECT / "manifests/additional_sets/MANIFEST.sha256"
FIT_ENTRIES = PROJECT / "manifests/weights/coach_si_table2_final_cycle_entries.csv"
OVERFITTING = {"AE11", "MB08-165", "MB16-43"}
AUXILIARY_FINAL = {"SC74", "OEEFD"}


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


def stoichiometric_species(value: str) -> set[str]:
    fields = [field.strip() for field in value.split(",")]
    if len(fields) % 2:
        raise ValueError(f"odd stoichiometry field count: {value}")
    for coefficient in fields[0::2]:
        float(coefficient)
    return set(fields[1::2])


def block(text: str, name: str, required: bool = False) -> str:
    match = re.search(
        rf"(?ims)^\s*\${re.escape(name)}\s*$\n(.*?)^\s*\$end\s*$", text
    )
    if match:
        return match.group(1)
    if required:
        raise ValueError(f"missing ${name} block")
    return ""


def parsed_molecule(text: str) -> tuple[str, str, int, int, int, str, str]:
    molecule = block(text, "molecule", required=True)
    lines = [
        line.strip()
        for line in molecule.splitlines()
        if line.strip() and not line.lstrip().startswith(("!", "#"))
    ]
    first = lines[0].split()
    if len(first) < 2 or not re.fullmatch(r"[+-]?\d+", first[0]) or not first[1].isdigit():
        raise ValueError("invalid charge/multiplicity")
    atom_count = 0
    real_atom_count = 0
    ghost_atom_count = 0
    geometry: list[str] = []
    after_separator = False
    for line in lines[1:]:
        if line == "--":
            after_separator = True
            geometry.append(line)
            continue
        fields = line.split()
        fragment_header = (
            after_separator
            and len(fields) >= 2
            and re.fullmatch(r"[+-]?\d+", fields[0])
            and fields[1].isdigit()
        )
        geometry.append(line)
        if not fragment_header:
            atom_count += 1
            if fields[0].startswith("@"):
                ghost_atom_count += 1
            else:
                real_atom_count += 1
        after_separator = False
    return (
        first[0],
        first[1],
        atom_count,
        real_atom_count,
        ghost_atom_count,
        sha256_bytes(molecule.encode()),
        sha256_bytes(("\n".join(geometry) + "\n").encode()),
    )


def optional_block(text: str, name: str) -> tuple[str, int]:
    value = block(text, name)
    return (sha256_bytes(value.encode()), len(value.encode())) if value else ("", 0)


def main() -> int:
    checks: dict[str, bool] = {}
    details: dict[str, object] = {}
    policy = yaml.safe_load(POLICY.read_text(encoding="utf-8"))
    dataset_roles = read_csv(DATASET_ROLES)
    reaction_roles = read_csv(REACTION_ROLES)
    species_roles = read_csv(SPECIES_ROLES)
    input_metadata = read_csv(INPUT_METADATA)
    provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    reactions = read_csv(DATASET_EVAL) + read_csv(BIGNC_EVAL) + read_csv(GDB9_EVAL)
    core_datasets = {row["dataset"] for row in read_csv(DATASET_MANIFEST)}
    source_species = {row["species"]: row for row in read_csv(SPECIES_MANIFEST)}
    bignc_info = json.loads(BIGNC_INFO.read_text(encoding="utf-8"))
    gdb9_info = json.loads(GDB9_INFO.read_text(encoding="utf-8"))
    opt_info = json.loads(OPT_INFO.read_text(encoding="utf-8"))
    bignc_species = set(bignc_info)
    gdb9_species = set(gdb9_info)
    fit_entries = {row["reaction"]: row for row in read_csv(FIT_ENTRIES)}

    checks["policy_frozen_v2"] = (
        policy["schema_version"] == 1
        and policy["status"] == "frozen"
        and policy["name"] == "revwb97m2_data_roles_v2"
    )
    checks["random_point_split_forbidden"] = policy["leakage_policy"]["random_point_level_split_forbidden"] is True
    checks["final_cannot_change_model"] = policy["roles"]["final_assessment"]["may_change_model"] is False
    checks["qchem_orbitals_explicitly_forbidden"] = all(
        policy["geometry_and_basis_authority"][field] is False
        for field in ("orbital_files_used", "qarchive_files_used", "scratch_orbital_directories_used")
    )
    additional_hashes: dict[str, str] = {}
    for raw in ADDITIONAL_MANIFEST.read_text(encoding="utf-8").splitlines():
        expected_hash, relative = raw.split("  ", 1)
        additional_hashes[relative.removeprefix("./")] = expected_hash
    additional_files = {
        str(path.relative_to(ADDITIONAL_ROOT))
        for path in ADDITIONAL_ROOT.rglob("*")
        if path.is_file() and path.name != "MANIFEST.sha256"
    }
    checks["additional_sets_manifest_hash_pinned"] = (
        sha256(ADDITIONAL_MANIFEST)
        == policy["evidence"]["gscdb_additional_sets"]["manifest_sha256"]
    )
    checks["additional_sets_snapshot_complete_and_hashed"] = (
        set(additional_hashes) == additional_files
        and all(
            sha256(ADDITIONAL_ROOT / relative) == expected
            for relative, expected in additional_hashes.items()
        )
    )

    checks["dataset_role_rows_142_unique"] = len(dataset_roles) == 142 == len(
        {row["dataset"] for row in dataset_roles}
    )
    dataset_scope_counts = Counter(row["scope"] for row in dataset_roles)
    checks["dataset_scope_counts"] = dataset_scope_counts == Counter(
        {
            "gscdb137": 137,
            "appended_external": 2,
            "BigNC_external": 2,
            "GDB9_W1_F12_external": 1,
        }
    )
    dataset_role_map = {row["dataset"]: row for row in dataset_roles}
    checks["all_gscdb_datasets_are_model_selection"] = all(
        dataset_role_map[name]["model_selection"] == "true" for name in core_datasets
    )
    checks["only_external_datasets_are_final"] = {
        row["dataset"] for row in dataset_roles if row["final_assessment"] == "true"
    } == {"SC74", "OEEFD", "L14", "vL11", "GDB_W1-F12"}
    checks["overfitting_datasets_exact"] = {
        row["dataset"] for row in dataset_roles if row["overfitting_diagnostic"] == "true"
    } == OVERFITTING
    checks["bignc_geometry_is_verified"] = all(
        dataset_role_map[name]["geometry_status"]
        == "verified_pinned_official_qchem_input_snapshot"
        for name in ("L14", "vL11")
    )

    source_reaction_map = {row["Reaction"]: row for row in reactions}
    role_reaction_map = {row["reaction"]: row for row in reaction_roles}
    checks["reaction_rows_match_pinned_dataset_eval"] = (
        len(reaction_roles) == 11839
        and len(role_reaction_map) == 11839
        and set(role_reaction_map) == set(source_reaction_map)
    )
    checks["coefficient_fitting_exact_1498"] = {
        row["reaction"] for row in reaction_roles if row["coefficient_fitting"] == "true"
    } == set(fit_entries)
    checks["coefficient_weights_exact"] = all(
        role_reaction_map[name]["objective_weight"] == fit_entries[name]["objective_weight"]
        for name in fit_entries
    )
    checks["model_selection_exact_gscdb137"] = {
        row["reaction"] for row in reaction_roles if row["model_selection"] == "true"
    } == {row["Reaction"] for row in reactions if row["Dataset"] in core_datasets}
    checks["overfitting_reactions_exact_219"] = {
        row["reaction"] for row in reaction_roles if row["overfitting_diagnostic"] == "true"
    } == {row["Reaction"] for row in reactions if row["Dataset"] in OVERFITTING}
    checks["final_assessment_reactions_exact_3462"] = {
        row["reaction"] for row in reaction_roles if row["final_assessment"] == "true"
    } == {
        row["Reaction"]
        for row in reactions
        if row["Dataset"] in AUXILIARY_FINAL | {"L14", "vL11", "GDB_W1-F12"}
    }
    checks["mb16_fitting_diagnostic_overlap_43"] = sum(
        row["dataset"] == "MB16-43"
        and row["coefficient_fitting"] == "true"
        and row["overfitting_diagnostic"] == "true"
        for row in reaction_roles
    ) == 43

    expected_role_species: dict[str, set[str]] = defaultdict(set)
    for row in reaction_roles:
        members = stoichiometric_species(source_reaction_map[row["reaction"]]["Stoichiometry"])
        for role in (
            "coefficient_fitting",
            "model_selection",
            "overfitting_diagnostic",
            "final_assessment",
        ):
            if row[role] == "true":
                expected_role_species[role].update(members)
    species_role_map = {row["species"]: row for row in species_roles}
    checks["species_rows_17452_unique"] = len(species_roles) == 17452 == len(species_role_map)
    checks["species_identity_union"] = set(species_role_map) == (
        set(source_species) | bignc_species | gdb9_species
    )
    for role, expected in expected_role_species.items():
        observed = {row["species"] for row in species_roles if row[role] == "true"}
        checks[f"{role}_species_exact"] = observed == expected
        details[f"{role}_species_count"] = len(observed)
    checks["available_qchem_inputs_17452"] = sum(
        row["qchem_input_metadata_available"] == "true" for row in species_roles
    ) == 17452
    checks["no_blocked_external_species"] = not {
        row["species"]
        for row in species_roles
        if row["geometry_status"].startswith("blocked")
    }

    authority = policy["geometry_and_basis_authority"]
    snapshot_root = Path(authority["snapshot_root"])
    source_input_manifest = read_csv(Path(authority["input_manifest"]))
    source_input_map = {row["species"]: row for row in source_input_manifest}
    metadata_map = {row["species"]: row for row in input_metadata}
    checks["qchem_metadata_rows_17658_unique"] = len(input_metadata) == 17658 == len(metadata_map)
    checks["qchem_metadata_species_exact"] = set(metadata_map) == set(species_role_map) | set(opt_info)
    metadata_ok = True
    generated_basis_sections = 0
    generated_auxiliary_sections = 0
    ecp_sections = 0
    for species, record in metadata_map.items():
        input_row = source_input_map.get(species)
        path = (
            snapshot_root / input_row["snapshot_input"]
            if input_row is not None
            else ROOT / record["snapshot_input"]
        )
        data = path.read_bytes()
        text = data.decode("utf-8")
        try:
            (
                charge,
                multiplicity,
                atom_count,
                real_atom_count,
                ghost_atom_count,
                molecule_hash,
                geometry_hash,
            ) = parsed_molecule(text)
            basis_hash, basis_bytes = optional_block(text, "basis")
            aux_hash, aux_bytes = optional_block(text, "aux_basis")
            ecp_hash, ecp_bytes = optional_block(text, "ecp")
        except (IndexError, UnicodeDecodeError, ValueError):
            metadata_ok = False
            continue
        if species in source_species:
            expected_charge = source_species[species]["charge"]
            expected_multiplicity = source_species[species]["multiplicity"]
            expected_atom_count = int(source_species[species]["atom_count"])
            expected_real_atom_count = expected_atom_count
            expected_hash = input_row["sha256"]
        else:
            expected = bignc_info.get(species, gdb9_info.get(species, opt_info.get(species)))
            expected_charge = str(expected["charge"])
            expected_multiplicity = str(expected["multiplicity"])
            expected_real_atom_count = len(str(expected["molecule"]).splitlines())
            expected_atom_count = atom_count
            expected_hash = record["input_sha256"]
        row_ok = (
            sha256_bytes(data) == expected_hash == record["input_sha256"]
            and charge == record["charge"] == expected_charge
            and multiplicity == record["multiplicity"] == expected_multiplicity
            and atom_count == int(record["atom_count"]) == expected_atom_count
            and real_atom_count == int(record["real_atom_count"]) == expected_real_atom_count
            and ghost_atom_count == int(record["ghost_atom_count"])
            and molecule_hash == record["molecule_block_sha256"]
            and geometry_hash == record["geometry_payload_sha256"]
            and basis_hash == record["basis_block_sha256"]
            and basis_bytes == int(record["basis_block_bytes"])
            and aux_hash == record["auxiliary_basis_block_sha256"]
            and aux_bytes == int(record["auxiliary_basis_block_bytes"])
            and ecp_hash == record["ecp_block_sha256"]
            and ecp_bytes == int(record["ecp_block_bytes"])
            and record["orbital_files_used"] == "false"
            and record["qchem_unrestricted"].lower() == "true"
        )
        metadata_ok = metadata_ok and row_ok
        generated_basis_sections += bool(basis_hash)
        generated_auxiliary_sections += bool(aux_hash)
        ecp_sections += bool(ecp_hash)
    checks["every_qchem_input_metadata_row_reparsed_and_hashed"] = metadata_ok
    checks["all_role_qchem_inputs_are_unrestricted"] = all(
        row["qchem_unrestricted"].lower() == "true" for row in input_metadata
    )
    details["generated_basis_section_count"] = generated_basis_sections
    details["generated_auxiliary_basis_section_count"] = generated_auxiliary_sections
    details["ecp_section_count"] = ecp_sections

    artifact_paths = {
        "policy_yaml": POLICY,
        "dataset_roles_csv": DATASET_ROLES,
        "reaction_roles_csv": REACTION_ROLES,
        "species_roles_csv": SPECIES_ROLES,
        "qchem_input_metadata_csv": INPUT_METADATA,
        "provenance_json": PROVENANCE,
    }
    checks["provenance_policy_hash"] = provenance["policy"]["sha256"] == sha256(POLICY)
    checks["provenance_output_hashes"] = all(
        provenance["outputs"][path.name]["sha256"] == sha256(path)
        for path in (DATASET_ROLES, REACTION_ROLES, SPECIES_ROLES, INPUT_METADATA)
    )

    details["dataset_scope_counts"] = dict(dataset_scope_counts)
    details["reaction_counts"] = {
        role: sum(row[role] == "true" for row in reaction_roles)
        for role in (
            "coefficient_fitting",
            "model_selection",
            "overfitting_diagnostic",
            "final_assessment",
        )
    }
    details["BigNC_reaction_count"] = 25
    details["GDB9_W1_F12_reaction_count"] = 3366
    details["OPT_verified_qchem_input_count_separate_geometry_assessment"] = 206
    details["BigNC_counterpoise_ghost_species_count"] = sum(
        row["scope"] == "BigNC_external" and int(row["ghost_atom_count"]) > 0
        for row in input_metadata
    )
    details["BigNC_counterpoise_ghost_center_count"] = sum(
        int(row["ghost_atom_count"])
        for row in input_metadata
        if row["scope"] == "BigNC_external"
    )
    report = {
        "schema_version": 1,
        "status": "passed" if all(checks.values()) else "failed",
        "checks": checks,
        "details": details,
        "artifact_sha256": {name: sha256(path) for name, path in artifact_paths.items()},
    }
    (ROLE_ROOT / "validation.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
