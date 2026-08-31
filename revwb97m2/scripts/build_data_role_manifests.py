#!/usr/bin/env python3
"""Build deterministic revwb97m2 data-role and Q-Chem input-metadata manifests."""

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
DATASET_EVAL = PROJECT / "manifests/gscdb137/source/DatasetEval.csv"
DATASETS = PROJECT / "manifests/gscdb137/dataset_manifest.csv"
SPECIES = PROJECT / "manifests/gscdb137/species_manifest.csv"
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
OVERFITTING_DATASETS = {"AE11", "MB08-165", "MB16-43"}
AUXILIARY_FINAL_DATASETS = {"SC74", "OEEFD"}
BIGNC_DATASETS = {"L14", "vL11"}
GDB9_DATASETS = {"GDB_W1-F12"}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_label(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict[str, dict[str, object]]:
    return json.loads(path.read_text(encoding="utf-8"))


def additional_manifest_hashes() -> dict[str, str]:
    hashes: dict[str, str] = {}
    for raw in ADDITIONAL_MANIFEST.read_text(encoding="utf-8").splitlines():
        expected, relative = raw.split("  ", 1)
        hashes[relative.removeprefix("./")] = expected
    return hashes


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty CSV: {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def parse_stoichiometry(value: str) -> list[str]:
    fields = [field.strip() for field in value.split(",")]
    if len(fields) % 2:
        raise ValueError(f"odd stoichiometry field count: {value}")
    species: list[str] = []
    for coefficient, name in zip(fields[0::2], fields[1::2], strict=True):
        float(coefficient)
        if not name:
            raise ValueError(f"empty species in stoichiometry: {value}")
        species.append(name)
    return species


def qchem_block(text: str, name: str, required: bool = False) -> str:
    match = re.search(
        rf"(?ims)^\s*\${re.escape(name)}\s*$\n(.*?)^\s*\$end\s*$", text
    )
    if match:
        return match.group(1)
    if required:
        raise ValueError(f"missing ${name} block")
    return ""


def rem_values(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in qchem_block(text, "rem", required=True).splitlines():
        line = raw.strip()
        if not line or line.startswith(("!", "#")):
            continue
        fields = line.replace("=", " ").split()
        if len(fields) >= 2:
            values[fields[0].upper()] = fields[1]
    return values


def molecule_metadata(text: str) -> dict[str, object]:
    molecule = qchem_block(text, "molecule", required=True)
    meaningful = [
        line.strip()
        for line in molecule.splitlines()
        if line.strip() and not line.lstrip().startswith(("!", "#"))
    ]
    if not meaningful:
        raise ValueError("empty $molecule block")
    first = meaningful[0].split()
    if len(first) < 2 or not re.fullmatch(r"[+-]?\d+", first[0]) or not first[1].isdigit():
        raise ValueError("missing leading charge and multiplicity")

    geometry_lines: list[str] = []
    elements: list[str] = []
    real_atom_count = 0
    ghost_atom_count = 0
    after_fragment_separator = False
    for line in meaningful[1:]:
        if line == "--":
            after_fragment_separator = True
            geometry_lines.append(line)
            continue
        fields = line.split()
        if (
            after_fragment_separator
            and len(fields) >= 2
            and re.fullmatch(r"[+-]?\d+", fields[0])
            and fields[1].isdigit()
        ):
            geometry_lines.append(line)
            after_fragment_separator = False
            continue
        after_fragment_separator = False
        match = re.match(r"@?([A-Za-z]{1,3})", fields[0])
        if not match:
            raise ValueError(f"unrecognized geometry line: {line}")
        elements.append(match.group(1).capitalize())
        if fields[0].startswith("@"):
            ghost_atom_count += 1
        else:
            real_atom_count += 1
        geometry_lines.append(line)

    return {
        "molecule_block_sha256": sha256_bytes(molecule.encode()),
        "geometry_payload_sha256": sha256_bytes(("\n".join(geometry_lines) + "\n").encode()),
        "charge": first[0],
        "multiplicity": first[1],
        "atom_count": len(elements),
        "real_atom_count": real_atom_count,
        "ghost_atom_count": ghost_atom_count,
        "elements": ";".join(sorted(set(elements))),
    }


def optional_block_metadata(text: str, name: str) -> tuple[str, int]:
    value = qchem_block(text, name)
    if not value:
        return "", 0
    data = value.encode()
    return sha256_bytes(data), len(data)


def build_roles() -> tuple[
    list[dict[str, object]],
    list[dict[str, object]],
    list[dict[str, object]],
    dict[str, set[str]],
]:
    core_reactions = read_csv(DATASET_EVAL)
    bignc_reactions = read_csv(BIGNC_EVAL)
    gdb9_reactions = read_csv(GDB9_EVAL)
    reactions = core_reactions + bignc_reactions + gdb9_reactions
    dataset_info = {row["dataset"]: row for row in read_csv(DATASETS)}
    fit_entries = read_csv(FIT_ENTRIES)
    fitting = {row["reaction"]: row for row in fit_entries}
    if len(fitting) != len(fit_entries):
        raise ValueError("Cycle-2 fitting reaction IDs are not unique")

    reaction_records: list[dict[str, object]] = []
    species_by_role: dict[str, set[str]] = {
        "coefficient_fitting": set(),
        "model_selection": set(),
        "overfitting_diagnostic": set(),
        "final_assessment": set(),
    }
    reaction_count = Counter(row["Dataset"] for row in reactions)
    fit_count = Counter(row["dataset_eval_dataset"] for row in fit_entries)

    for row in reactions:
        reaction = row["Reaction"]
        dataset = row["Dataset"]
        members = parse_stoichiometry(row["Stoichiometry"])
        is_core = dataset in dataset_info
        is_auxiliary_final = dataset in AUXILIARY_FINAL_DATASETS
        is_bignc = dataset in BIGNC_DATASETS
        is_gdb9 = dataset in GDB9_DATASETS
        if not (is_core or is_auxiliary_final or is_bignc or is_gdb9):
            raise ValueError(f"unclassified DatasetEval group: {dataset}")
        is_fit = reaction in fitting
        is_model_selection = is_core
        is_overfitting = dataset in OVERFITTING_DATASETS
        is_final = is_auxiliary_final or is_bignc or is_gdb9
        flags = {
            "coefficient_fitting": is_fit,
            "model_selection": is_model_selection,
            "overfitting_diagnostic": is_overfitting,
            "final_assessment": is_final,
        }
        for role, enabled in flags.items():
            if enabled:
                species_by_role[role].update(members)
        reaction_records.append(
            {
                "reaction": reaction,
                "dataset": dataset,
                "scope": (
                    "gscdb137"
                    if is_core
                    else "appended_external"
                    if is_auxiliary_final
                    else "BigNC_external"
                    if is_bignc
                    else "GDB9_W1_F12_external"
                ),
                "coefficient_fitting": bool_text(is_fit),
                "model_selection": bool_text(is_model_selection),
                "overfitting_diagnostic": bool_text(is_overfitting),
                "final_assessment": bool_text(is_final),
                "objective_weight": fitting[reaction]["objective_weight"] if is_fit else "",
                "stoichiometric_species_count": len(members),
            }
        )

    dataset_records: list[dict[str, object]] = []
    for dataset, info in dataset_info.items():
        is_overfitting = dataset in OVERFITTING_DATASETS
        dataset_records.append(
            {
                "dataset": dataset,
                "scope": "gscdb137",
                "category": info["category_short"],
                "reaction_count": reaction_count[dataset],
                "coefficient_fitting_count": fit_count[dataset],
                "coefficient_fitting": bool_text(fit_count[dataset] > 0),
                "model_selection": "true",
                "overfitting_diagnostic": bool_text(is_overfitting),
                "final_assessment": "false",
                "geometry_status": "verified_qchem_input_snapshot",
                "notes": (
                    "MB16-43 also fits coefficients; diagnostic is not independent"
                    if dataset == "MB16-43"
                    else ""
                ),
            }
        )
    for dataset in sorted(AUXILIARY_FINAL_DATASETS):
        dataset_records.append(
            {
                "dataset": dataset,
                "scope": "appended_external",
                "category": "EF" if dataset == "OEEFD" else "MIXED",
                "reaction_count": reaction_count[dataset],
                "coefficient_fitting_count": 0,
                "coefficient_fitting": "false",
                "model_selection": "false",
                "overfitting_diagnostic": "false",
                "final_assessment": "true",
                "geometry_status": "verified_qchem_input_snapshot",
                "notes": "evaluate once after model and sparsity are frozen",
            }
        )
    for dataset, expected in (("L14", 14), ("vL11", 11)):
        dataset_records.append(
            {
                "dataset": dataset,
                "scope": "BigNC_external",
                "category": "NC",
                "reaction_count": expected,
                "coefficient_fitting_count": 0,
                "coefficient_fitting": "false",
                "model_selection": "false",
                "overfitting_diagnostic": "false",
                "final_assessment": "true",
                "geometry_status": "verified_pinned_official_qchem_input_snapshot",
                "notes": (
                    "post-freeze only; COACH itself tuned D4-ATM on L14/vL11, "
                    "so BigNC is untouched here only if no revwb97m2 parameter uses it"
                ),
            }
        )
    dataset_records.append(
        {
            "dataset": "GDB_W1-F12",
            "scope": "GDB9_W1_F12_external",
            "category": "TC",
            "reaction_count": reaction_count["GDB_W1-F12"],
            "coefficient_fitting_count": 0,
            "coefficient_fitting": "false",
            "model_selection": "false",
            "overfitting_diagnostic": "false",
            "final_assessment": "true",
            "geometry_status": "verified_pinned_official_qchem_input_snapshot",
            "notes": "untouched post-freeze robustness test; MAE, MSE, and SD",
        }
    )

    manifest_species = read_csv(SPECIES)
    manifest_by_name = {row["species"]: row for row in manifest_species}
    species_records: list[dict[str, object]] = []
    for name, row in manifest_by_name.items():
        flags = {role: name in names for role, names in species_by_role.items()}
        if not any(flags.values()):
            raise ValueError(f"species is not required by any locked role: {name}")
        species_records.append(
            {
                "species": name,
                "scope": row["scope"],
                "coefficient_fitting": bool_text(flags["coefficient_fitting"]),
                "model_selection": bool_text(flags["model_selection"]),
                "overfitting_diagnostic": bool_text(flags["overfitting_diagnostic"]),
                "final_assessment": bool_text(flags["final_assessment"]),
                "qchem_input_metadata_available": "true",
                "geometry_status": "verified_qchem_input_snapshot",
            }
        )

    external_info = {
        "BigNC_external": read_json(BIGNC_INFO),
        "GDB9_W1_F12_external": read_json(GDB9_INFO),
    }
    for scope, entries in external_info.items():
        for name in sorted(entries):
            if name in manifest_by_name:
                raise ValueError(
                    f"external species collides with GSCDB input identity: {name}"
                )
            species_by_role["final_assessment"].add(name)
            species_records.append(
                {
                    "species": name,
                    "scope": scope,
                    "coefficient_fitting": "false",
                    "model_selection": "false",
                    "overfitting_diagnostic": "false",
                    "final_assessment": "true",
                    "qchem_input_metadata_available": "true",
                    "geometry_status": "verified_pinned_official_qchem_input_snapshot",
                }
            )
    return dataset_records, reaction_records, species_records, species_by_role


def build_qchem_metadata(
    policy: dict[str, object], species_records: list[dict[str, object]]
) -> list[dict[str, object]]:
    authority = policy["geometry_and_basis_authority"]
    snapshot_root = Path(authority["snapshot_root"])
    input_manifest_path = Path(authority["input_manifest"])
    completion = json.loads(Path(authority["completion_marker"]).read_text(encoding="utf-8"))
    validation = json.loads(Path(authority["validation_record"]).read_text(encoding="utf-8"))
    if sha256(input_manifest_path) != authority["input_manifest_sha256"]:
        raise ValueError("immutable Q-Chem input manifest hash mismatch")
    if completion["status"] != "complete" or validation["status"] != "pass":
        raise ValueError("immutable Q-Chem input snapshot is not complete and valid")
    if completion["input_manifest_sha256"] != sha256(input_manifest_path):
        raise ValueError("completion marker does not match Q-Chem input manifest")

    source_species = {row["species"]: row for row in read_csv(SPECIES)}
    role_by_species = {row["species"]: row for row in species_records}
    input_rows = read_csv(input_manifest_path)
    records: list[dict[str, object]] = []
    for row in input_rows:
        species = row["species"]
        if species not in source_species or species not in role_by_species:
            raise ValueError(f"unexpected Q-Chem input species: {species}")
        path = snapshot_root / row["snapshot_input"]
        data = path.read_bytes()
        if sha256_bytes(data) != row["sha256"]:
            raise ValueError(f"Q-Chem input hash mismatch: {species}")
        text = data.decode("utf-8")
        rem = rem_values(text)
        molecule = molecule_metadata(text)
        manifest = source_species[species]
        if molecule["charge"] != manifest["charge"] or molecule["multiplicity"] != manifest["multiplicity"]:
            raise ValueError(f"charge/multiplicity mismatch: {species}")
        if molecule["atom_count"] != int(manifest["atom_count"]):
            raise ValueError(
                f"atom-count mismatch for {species}: input={molecule['atom_count']} manifest={manifest['atom_count']}"
            )
        basis_hash, basis_bytes = optional_block_metadata(text, "basis")
        aux_hash, aux_bytes = optional_block_metadata(text, "aux_basis")
        ecp_hash, ecp_bytes = optional_block_metadata(text, "ecp")
        roles = role_by_species[species]
        records.append(
            {
                "species": species,
                "scope": row["scope"],
                "snapshot_input": row["snapshot_input"],
                "input_sha256": row["sha256"],
                "molecule_block_sha256": molecule["molecule_block_sha256"],
                "geometry_payload_sha256": molecule["geometry_payload_sha256"],
                "charge": molecule["charge"],
                "multiplicity": molecule["multiplicity"],
                "atom_count": molecule["atom_count"],
                "real_atom_count": molecule["real_atom_count"],
                "ghost_atom_count": molecule["ghost_atom_count"],
                "elements": molecule["elements"],
                "manifest_orbital_basis": manifest["basis"],
                "qchem_rem_basis": rem.get("BASIS", ""),
                "basis_block_sha256": basis_hash,
                "basis_block_bytes": basis_bytes,
                "manifest_auxiliary_basis": manifest["aux_basis_corr"],
                "qchem_rem_auxiliary_basis": rem.get("AUX_BASIS_CORR", ""),
                "auxiliary_basis_block_sha256": aux_hash,
                "auxiliary_basis_block_bytes": aux_bytes,
                "qchem_rem_ecp": rem.get("ECP", ""),
                "ecp_block_sha256": ecp_hash,
                "ecp_block_bytes": ecp_bytes,
                "coefficient_fitting": roles["coefficient_fitting"],
                "model_selection": roles["model_selection"],
                "overfitting_diagnostic": roles["overfitting_diagnostic"],
                "final_assessment": roles["final_assessment"],
                "qchem_unrestricted": rem.get("UNRESTRICTED", ""),
                "orbital_files_used": "false",
            }
        )

    external_sets = (
        ("BigNC_external", ADDITIONAL_ROOT / "BigNC", read_json(BIGNC_INFO)),
        (
            "GDB9_W1_F12_external",
            ADDITIONAL_ROOT / "GDB9-W1-F12",
            read_json(GDB9_INFO),
        ),
        ("OPT_external", ADDITIONAL_ROOT / "OPT", read_json(OPT_INFO)),
    )
    source_hashes = additional_manifest_hashes()
    for scope, source_root, metadata in external_sets:
        for species, manifest in sorted(metadata.items()):
            path = source_root / "qchem_inputs" / f"{species}.in"
            relative = str(path.relative_to(ADDITIONAL_ROOT))
            data = path.read_bytes()
            if sha256_bytes(data) != source_hashes[relative]:
                raise ValueError(f"pinned AdditionalSets input hash mismatch: {species}")
            text = data.decode("utf-8")
            rem = rem_values(text)
            molecule = molecule_metadata(text)
            if molecule["charge"] != str(manifest["charge"]):
                raise ValueError(f"external charge mismatch: {species}")
            if molecule["multiplicity"] != str(manifest["multiplicity"]):
                raise ValueError(f"external multiplicity mismatch: {species}")
            if molecule["real_atom_count"] != len(str(manifest["molecule"]).splitlines()):
                raise ValueError(f"external atom-count mismatch: {species}")
            if rem.get("BASIS", "").lower() != str(manifest["basis"]).lower():
                raise ValueError(f"external basis mismatch: {species}")
            basis_hash, basis_bytes = optional_block_metadata(text, "basis")
            aux_hash, aux_bytes = optional_block_metadata(text, "aux_basis")
            ecp_hash, ecp_bytes = optional_block_metadata(text, "ecp")
            roles = role_by_species.get(
                species,
                {
                    "coefficient_fitting": "false",
                    "model_selection": "false",
                    "overfitting_diagnostic": "false",
                    "final_assessment": "false",
                },
            )
            records.append(
                {
                    "species": species,
                    "scope": scope,
                    "snapshot_input": str(path),
                    "input_sha256": sha256_bytes(data),
                    "molecule_block_sha256": molecule["molecule_block_sha256"],
                    "geometry_payload_sha256": molecule["geometry_payload_sha256"],
                    "charge": molecule["charge"],
                    "multiplicity": molecule["multiplicity"],
                    "atom_count": molecule["atom_count"],
                    "real_atom_count": molecule["real_atom_count"],
                    "ghost_atom_count": molecule["ghost_atom_count"],
                    "elements": molecule["elements"],
                    "manifest_orbital_basis": manifest["basis"],
                    "qchem_rem_basis": rem.get("BASIS", ""),
                    "basis_block_sha256": basis_hash,
                    "basis_block_bytes": basis_bytes,
                    "manifest_auxiliary_basis": "",
                    "qchem_rem_auxiliary_basis": rem.get("AUX_BASIS_CORR", ""),
                    "auxiliary_basis_block_sha256": aux_hash,
                    "auxiliary_basis_block_bytes": aux_bytes,
                    "qchem_rem_ecp": rem.get("ECP", ""),
                    "ecp_block_sha256": ecp_hash,
                    "ecp_block_bytes": ecp_bytes,
                    "coefficient_fitting": roles["coefficient_fitting"],
                    "model_selection": roles["model_selection"],
                    "overfitting_diagnostic": roles["overfitting_diagnostic"],
                    "final_assessment": roles["final_assessment"],
                    "qchem_unrestricted": rem.get("UNRESTRICTED", ""),
                    "orbital_files_used": "false",
                }
            )
    return records


def main() -> int:
    policy = yaml.safe_load(POLICY.read_text(encoding="utf-8"))
    for evidence in ("coach_main", "coach_si", "dataset_eval", "standard_errors"):
        record = policy["evidence"][evidence]
        if sha256(ROOT / record["path"]) != record["sha256"]:
            raise ValueError(f"evidence hash mismatch: {evidence}")

    datasets, reactions, species, species_by_role = build_roles()
    qchem_metadata = build_qchem_metadata(policy, species)
    ROLE_ROOT.mkdir(parents=True, exist_ok=True)
    outputs = {
        "dataset_roles.csv": datasets,
        "reaction_roles.csv": reactions,
        "species_roles.csv": species,
        "qchem_input_metadata.csv": qchem_metadata,
    }
    for name, rows in outputs.items():
        write_csv(ROLE_ROOT / name, rows)

    role_counts = {
        role: {
            "reaction_count": sum(row[role] == "true" for row in reactions),
            "species_count": len(names),
        }
        for role, names in species_by_role.items()
    }
    provenance = {
        "schema_version": 1,
        "status": "generated_pending_independent_validation",
        "policy": {
            "path": str(POLICY.relative_to(ROOT)),
            "sha256": sha256(POLICY),
        },
        "sources": {
            source_label(path): sha256(path)
            for path in (
                DATASET_EVAL,
                DATASETS,
                SPECIES,
                BIGNC_SPECIES,
                FIT_ENTRIES,
                BIGNC_EVAL,
                BIGNC_INFO,
                GDB9_EVAL,
                GDB9_INFO,
                OPT_INFO,
                ADDITIONAL_MANIFEST,
            )
        },
        "qchem_input_authority": {
            "input_manifest": policy["geometry_and_basis_authority"]["input_manifest"],
            "input_manifest_sha256": sha256(
                Path(policy["geometry_and_basis_authority"]["input_manifest"])
            ),
            "orbital_files_used": False,
        },
        "outputs": {
            name: {"rows": len(rows), "sha256": sha256(ROLE_ROOT / name)}
            for name, rows in outputs.items()
        },
        "role_counts": role_counts,
        "known_limitations": [
            "GSCDB137 model selection overlaps the coefficient-fitting data by design",
            "MB16-43 is both coefficient-fitting and an overfitting diagnostic",
            "COACH tuned its D4-ATM parameters on BigNC; revwb97m2 may call BigNC final only if it never tunes any parameter on L14/vL11",
            "OPT has verified inputs but is a separate geometry-optimization assessment outside this fixed-geometry energy role table",
        ],
    }
    write_json(ROLE_ROOT / "provenance.json", provenance)
    print(json.dumps({"outputs": provenance["outputs"], "role_counts": role_counts}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
