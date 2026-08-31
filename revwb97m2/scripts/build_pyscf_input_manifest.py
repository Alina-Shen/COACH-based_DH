#!/usr/bin/env python3
"""Build deterministic all-UKS PySCF molecular-input records from verified inputs."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
from collections import Counter, defaultdict
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "revwb97m2"
POLICY = PROJECT / "manifests/pyscf_inputs/pyscf_input_policy_v2.yaml"
QCHEM_METADATA = PROJECT / "manifests/data_roles/qchem_input_metadata.csv"
SPECIES_ROLES = PROJECT / "manifests/data_roles/species_roles.csv"
REACTION_ROLES = PROJECT / "manifests/data_roles/reaction_roles.csv"
CORE_INPUT_ROOT = Path(
    "/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/"
    "authoritative_inputs/qchem/gscdb137_v1"
)
ADDITIONAL_ROOT = Path(
    "/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/"
    "authoritative_inputs/qchem/additionalsets_gscdb_8f2c7e5"
)
REACTION_SOURCES = (
    PROJECT / "manifests/gscdb137/source/DatasetEval.csv",
    ADDITIONAL_ROOT / "BigNC/DatasetEval.csv",
    ADDITIONAL_ROOT / "GDB9-W1-F12/DatasetEval.csv",
)
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


def meaningful_lines(block: str) -> list[str]:
    return [
        line.strip()
        for line in block.splitlines()
        if line.strip() and not line.lstrip().startswith(("!", "#"))
    ]


def parse_molecule(text: str) -> dict[str, object]:
    molecule = qchem_block(text, "molecule", required=True)
    lines = meaningful_lines(molecule)
    header = lines[0].split()
    if len(header) < 2 or not re.fullmatch(r"[+-]?\d+", header[0]) or not header[1].isdigit():
        raise ValueError("invalid charge/multiplicity header")
    source_geometry: list[str] = []
    pyscf_geometry: list[str] = []
    real_atoms = 0
    ghost_atoms = 0
    elements: set[str] = set()
    after_separator = False
    for line in lines[1:]:
        if line == "--":
            after_separator = True
            continue
        fields = line.split()
        if (
            after_separator
            and len(fields) >= 2
            and re.fullmatch(r"[+-]?\d+", fields[0])
            and fields[1].isdigit()
        ):
            after_separator = False
            continue
        after_separator = False
        if len(fields) < 4:
            raise ValueError(f"non-Cartesian geometry line: {line}")
        for coordinate in fields[1:4]:
            float(coordinate)
        match = re.fullmatch(r"(@?)([A-Za-z]{1,3})", fields[0])
        if not match:
            raise ValueError(f"unsupported atom label: {fields[0]}")
        is_ghost = bool(match.group(1))
        element = match.group(2).capitalize()
        elements.add(element)
        if is_ghost:
            ghost_atoms += 1
            pyscf_label = f"Ghost-{element}"
        else:
            real_atoms += 1
            pyscf_label = element
        source_geometry.append(line)
        pyscf_geometry.append(" ".join([pyscf_label, *fields[1:]]))
    source_payload = "\n".join(source_geometry) + "\n"
    pyscf_atom = "\n".join(pyscf_geometry)
    return {
        "charge": int(header[0]),
        "multiplicity": int(header[1]),
        "spin": int(header[1]) - 1,
        "real_atom_count": real_atoms,
        "ghost_atom_count": ghost_atoms,
        "elements": sorted(elements),
        "molecule_block_sha256": sha256_bytes(molecule.encode()),
        "geometry_payload_sha256": sha256_bytes(source_payload.encode()),
        "pyscf_atom": pyscf_atom,
        "pyscf_atom_sha256": sha256_bytes((pyscf_atom + "\n").encode()),
    }


def parse_stoichiometry(value: str) -> list[str]:
    fields = [field.strip() for field in value.split(",")]
    if len(fields) % 2:
        raise ValueError(f"odd stoichiometry field count: {value}")
    for coefficient in fields[0::2]:
        float(coefficient)
    return fields[1::2]


def source_input_path(row: dict[str, str]) -> Path:
    path = Path(row["snapshot_input"])
    return path if path.is_absolute() else CORE_INPUT_ROOT / path


def block_record(text: str, block_name: str) -> dict[str, object]:
    value = qchem_block(text, block_name)
    return {
        "present": bool(value),
        "sha256": sha256_bytes(value.encode()) if value else "",
        "bytes": len(value.encode()),
        "qchem_block": value,
    }


def basis_source(label: str, block: dict[str, object], kind: str) -> tuple[str, str]:
    if block["present"]:
        return f"embedded_qchem_{kind}_block", "pending_step_6_generated_block_translation"
    if label:
        return f"named_qchem_{kind}_label", "pending_step_6_alias_validation"
    return "not_specified_in_source", "unassigned_pending_step_6"


def dataset_membership() -> dict[str, set[str]]:
    membership: dict[str, set[str]] = defaultdict(set)
    for path in REACTION_SOURCES:
        for row in read_csv(path):
            for species in parse_stoichiometry(row["Stoichiometry"]):
                membership[species].add(row["Dataset"])
    return membership


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output = args.output_dir.resolve()
    if output.exists() and any(output.iterdir()):
        raise SystemExit(f"refusing nonempty output directory: {output}")
    output.mkdir(parents=True, exist_ok=True)

    policy = yaml.safe_load(POLICY.read_text(encoding="utf-8"))
    metadata_rows = read_csv(QCHEM_METADATA)
    role_rows = {row["species"]: row for row in read_csv(SPECIES_ROLES)}
    memberships = dataset_membership()
    if len(metadata_rows) != policy["scope"]["qchem_metadata_records"]:
        raise ValueError("Q-Chem metadata count does not match frozen policy")

    index_rows: list[dict[str, object]] = []
    role_counts = Counter()
    scope_counts = Counter()
    orbital_sources = Counter()
    auxiliary_sources = Counter()
    ecp_sources = Counter()
    ghost_species = 0
    ghost_centers = 0
    records_path = output / policy["output"]["records"]
    with records_path.open("w", encoding="utf-8", newline="\n") as records_handle:
        for line_number, metadata in enumerate(sorted(metadata_rows, key=lambda row: row["species"]), 1):
            species = metadata["species"]
            source = source_input_path(metadata)
            data = source.read_bytes()
            if sha256_bytes(data) != metadata["input_sha256"]:
                raise ValueError(f"source input hash mismatch: {species}")
            text = data.decode("utf-8")
            molecule = parse_molecule(text)
            for field in ("charge", "multiplicity", "real_atom_count", "ghost_atom_count"):
                if str(molecule[field]) != metadata[field]:
                    raise ValueError(f"{field} mismatch: {species}")
            for field in ("molecule_block_sha256", "geometry_payload_sha256"):
                if molecule[field] != metadata[field]:
                    raise ValueError(f"{field} mismatch: {species}")
            if metadata["qchem_unrestricted"].lower() != "true":
                raise ValueError(f"source is not unrestricted: {species}")

            basis_block = block_record(text, "basis")
            auxiliary_block = block_record(text, "aux_basis")
            ecp_block = block_record(text, "ecp")
            orbital_source, orbital_status = basis_source(
                metadata["qchem_rem_basis"], basis_block, "orbital_basis"
            )
            auxiliary_source, auxiliary_status = basis_source(
                metadata["qchem_rem_auxiliary_basis"], auxiliary_block, "auxiliary_basis"
            )
            ecp_source, ecp_status = basis_source(metadata["qchem_rem_ecp"], ecp_block, "ecp")
            if not ecp_block["present"] and not metadata["qchem_rem_ecp"]:
                ecp_status = "not_applicable"

            role_row = role_rows.get(species)
            roles = {
                role: bool(role_row and role_row[role] == "true") for role in ROLE_NAMES
            }
            for role, enabled in roles.items():
                role_counts[role] += enabled
            required_for_energy = any(roles.values())
            datasets = sorted(memberships.get(species, set()))
            if metadata["scope"] == "OPT_external":
                datasets = ["W4-11-GEOM" if species.startswith("W4-11-GEOM_") else "SE"]
            if required_for_energy and not datasets:
                raise ValueError(f"energy-role species has no dataset membership: {species}")

            record = {
                "schema_version": 1,
                "identity": {
                    "species": species,
                    "scope": metadata["scope"],
                    "datasets": datasets,
                    "roles": roles,
                    "required_for_energy_roles": required_for_energy,
                    "evaluation_track": "fixed_geometry_energy" if required_for_energy else "geometry_optimization",
                },
                "pyscf_molecule": {
                    "atom": molecule["pyscf_atom"],
                    "unit": policy["pyscf_molecule"]["unit"],
                    "charge": molecule["charge"],
                    "multiplicity": molecule["multiplicity"],
                    "spin": molecule["spin"],
                    "real_atom_count": molecule["real_atom_count"],
                    "ghost_atom_count": molecule["ghost_atom_count"],
                    "elements": molecule["elements"],
                    "atom_sha256": molecule["pyscf_atom_sha256"],
                },
                "reference": {
                    "scf_class": "UKS",
                    "post_scf_mp2_class": "UMP2",
                    "unrestricted": True,
                    "exceptions_allowed": False,
                    "policy": "all_species_all_multiplicities",
                },
                "orbital_basis": {
                    "manifest_label": metadata["manifest_orbital_basis"],
                    "qchem_rem_label": metadata["qchem_rem_basis"],
                    "source_kind": orbital_source,
                    "translation_status": orbital_status,
                    "embedded_block": basis_block,
                },
                "auxiliary_basis": {
                    "manifest_label": metadata["manifest_auxiliary_basis"],
                    "qchem_rem_label": metadata["qchem_rem_auxiliary_basis"],
                    "source_kind": auxiliary_source,
                    "translation_status": auxiliary_status,
                    "embedded_block": auxiliary_block,
                },
                "ecp": {
                    "qchem_rem_label": metadata["qchem_rem_ecp"],
                    "source_kind": ecp_source,
                    "translation_status": ecp_status,
                    "embedded_block": ecp_block,
                },
                "provenance": {
                    "qchem_source_input": str(source),
                    "qchem_source_input_sha256": metadata["input_sha256"],
                    "qchem_molecule_block_sha256": molecule["molecule_block_sha256"],
                    "qchem_geometry_payload_sha256": molecule["geometry_payload_sha256"],
                    "qchem_orbitals_used": False,
                    "qarchive_used": False,
                },
                "runnable_status": "blocked_pending_step_6_basis_bridge_validation",
            }
            payload = json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
            record_sha = sha256_bytes(payload.encode())
            record["record_sha256"] = record_sha
            records_handle.write(
                json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"
            )

            scope_counts[metadata["scope"]] += 1
            orbital_sources[orbital_source] += 1
            auxiliary_sources[auxiliary_source] += 1
            ecp_sources[ecp_source] += 1
            ghost_species += molecule["ghost_atom_count"] > 0
            ghost_centers += molecule["ghost_atom_count"]
            index_rows.append(
                {
                    "line_number": line_number,
                    "species": species,
                    "scope": metadata["scope"],
                    "datasets": ";".join(datasets),
                    **{role: str(roles[role]).lower() for role in ROLE_NAMES},
                    "required_for_energy_roles": str(required_for_energy).lower(),
                    "evaluation_track": record["identity"]["evaluation_track"],
                    "charge": molecule["charge"],
                    "multiplicity": molecule["multiplicity"],
                    "spin": molecule["spin"],
                    "scf_class": "UKS",
                    "post_scf_mp2_class": "UMP2",
                    "real_atom_count": molecule["real_atom_count"],
                    "ghost_atom_count": molecule["ghost_atom_count"],
                    "elements": ";".join(molecule["elements"]),
                    "orbital_basis_label": metadata["manifest_orbital_basis"],
                    "orbital_basis_source": orbital_source,
                    "auxiliary_basis_label": metadata["manifest_auxiliary_basis"],
                    "auxiliary_basis_source": auxiliary_source,
                    "ecp_source": ecp_source,
                    "translation_status": "pending_step_6_basis_bridge_validation",
                    "source_input": str(source),
                    "source_input_sha256": metadata["input_sha256"],
                    "pyscf_atom_sha256": molecule["pyscf_atom_sha256"],
                    "record_sha256": record_sha,
                }
            )

    index_path = output / policy["output"]["index"]
    with index_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(index_rows[0]))
        writer.writeheader()
        writer.writerows(index_rows)
    shutil.copyfile(POLICY, output / "policy.yaml")

    sources = {
        str(path.relative_to(ROOT)): sha256(path)
        for path in (POLICY, QCHEM_METADATA, SPECIES_ROLES, REACTION_ROLES)
    }
    sources.update({str(path): sha256(path) for path in REACTION_SOURCES[1:]})
    provenance = {
        "schema_version": 1,
        "status": "generated_pending_independent_validation",
        "builder": str(Path(__file__).relative_to(ROOT)),
        "builder_sha256": sha256(Path(__file__)),
        "sources": sources,
        "counts": {
            "records": len(index_rows),
            "energy_role_species": sum(row["required_for_energy_roles"] == "true" for row in index_rows),
            "opt_geometry_species": sum(row["scope"] == "OPT_external" for row in index_rows),
            "scope": dict(scope_counts),
            "roles": dict(role_counts),
            "ghost_species": ghost_species,
            "ghost_centers": ghost_centers,
            "orbital_basis_source": dict(orbital_sources),
            "auxiliary_basis_source": dict(auxiliary_sources),
            "ecp_source": dict(ecp_sources),
        },
        "outputs": {
            records_path.name: {"bytes": records_path.stat().st_size, "sha256": sha256(records_path)},
            index_path.name: {"bytes": index_path.stat().st_size, "sha256": sha256(index_path)},
            "policy.yaml": {"bytes": (output / "policy.yaml").stat().st_size, "sha256": sha256(output / "policy.yaml")},
        },
        "qchem_orbitals_used": False,
        "basis_bridge_status": "pending_step_6_semantic_translation_and_validation",
    }
    (output / "provenance.json").write_text(
        json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(provenance["counts"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
