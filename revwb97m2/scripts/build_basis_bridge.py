#!/usr/bin/env python3
"""Build the lightweight Step-6 Q-Chem-metadata-to-PySCF basis index."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import yaml
from pyscf.data.elements import charge as nuclear_charge

from pyscf_basis_bridge import (
    QCHEM_AUXILIARY_FILES,
    canonical_hash,
    resolve_record,
)


ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "revwb97m2"
POLICY_PATH = PROJECT / "manifests/basis_bridge/step6_basis_bridge_v1.yaml"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def shell_dimensions(basis: list[Any]) -> tuple[int, int]:
    shells = len(basis)
    spherical_aos = sum((2 * shell[0] + 1) * (len(shell[1]) - 1) for shell in basis)
    return shells, spherical_aos


def atom_labels(atom: str) -> list[tuple[str, bool]]:
    labels: list[tuple[str, bool]] = []
    for line in atom.splitlines():
        label = line.split()[0]
        ghost = label.lower().startswith("ghost-")
        element = label.split("-", 1)[1] if ghost else label
        labels.append((element.capitalize(), ghost))
    return labels


def molecular_dimensions(
    atom: str, charge: int, basis: dict[str, list[Any]], ecp: dict[str, list[Any]]
) -> dict[str, int]:
    nbas = nao = electrons = ecp_electrons = 0
    for element, ghost in atom_labels(atom):
        shells, aos = shell_dimensions(basis[element])
        nbas += shells
        nao += aos
        if not ghost:
            electrons += nuclear_charge(element)
            if element in ecp:
                removed = int(ecp[element][0])
                electrons -= removed
                ecp_electrons += removed
    electrons -= charge
    return {"nbas": nbas, "nao": nao, "electrons": electrons, "ecp_electrons": ecp_electrons}


def main() -> int:
    policy = yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8"))
    source_root = Path(policy["source_snapshot"]["root"])
    records_path = source_root / policy["source_snapshot"]["records"]
    if sha256(source_root / "MANIFEST.sha256") != policy["source_snapshot"]["checksum_manifest_sha256"]:
        raise ValueError("immutable Step-5 checksum-manifest hash mismatch")
    if sha256(records_path) != policy["source_snapshot"]["records_sha256"]:
        raise ValueError("immutable Step-5 record hash mismatch")
    for name, metadata in policy["translation"]["qchem_auxiliary_library"]["files"].items():
        path = QCHEM_AUXILIARY_FILES[name]
        if path.name != metadata["path"] or sha256(path) != metadata["sha256"]:
            raise ValueError(f"Q-Chem auxiliary-library hash mismatch: {name}")

    records = [json.loads(line) for line in records_path.read_text(encoding="utf-8").splitlines()]
    if len(records) != policy["source_snapshot"]["record_count"]:
        raise ValueError("unexpected Step-5 record count")

    output_path = ROOT / policy["outputs"]["records"]
    provenance_path = ROOT / policy["outputs"]["provenance"]
    fields = [
        "species", "scope", "required_for_energy_roles", "source_record_sha256",
        "qchem_source_input_sha256", "elements", "spin", "orbital_qchem_label",
        "orbital_resolution", "orbital_pyscf_name", "orbital_definition_sha256",
        "auxiliary_qchem_label", "auxiliary_resolution", "auxiliary_pyscf_name",
        "auxiliary_definition_sha256", "ecp_resolution", "ecp_definition_sha256",
        "electron_count", "ecp_electrons", "orbital_shells", "orbital_spherical_aos",
        "auxiliary_shells", "auxiliary_spherical_aos", "runnable_status",
    ]
    counters: dict[str, Counter[str]] = {
        "orbital_resolution": Counter(),
        "auxiliary_resolution": Counter(),
        "ecp_resolution": Counter(),
        "scope": Counter(),
    }
    rows: list[dict[str, object]] = []
    definition_cache: dict[tuple[object, ...], tuple[dict[str, Any], str, str, str]] = {}
    for record in records:
        molecule = record["pyscf_molecule"]
        definition_key = (
            record["orbital_basis"]["embedded_block"]["sha256"],
            record["orbital_basis"]["qchem_rem_label"],
            record["auxiliary_basis"]["embedded_block"]["sha256"],
            record["auxiliary_basis"]["qchem_rem_label"],
            record["ecp"]["embedded_block"]["sha256"],
            tuple(molecule["elements"]),
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
        orbital_basis = resolved["orbital_basis"]
        auxiliary_basis = resolved["auxiliary_basis"]
        ecp = resolved["ecp"]
        orbital_dims = molecular_dimensions(molecule["atom"], molecule["charge"], orbital_basis, ecp)
        auxiliary_dims = molecular_dimensions(molecule["atom"], molecule["charge"], auxiliary_basis, {})
        if orbital_dims["electrons"] < 0 or (orbital_dims["electrons"] - molecule["spin"]) % 2:
            raise ValueError(f"electron/spin inconsistency: {record['identity']['species']}")
        row = {
            "species": record["identity"]["species"],
            "scope": record["identity"]["scope"],
            "required_for_energy_roles": str(record["identity"]["required_for_energy_roles"]).lower(),
            "source_record_sha256": record["record_sha256"],
            "qchem_source_input_sha256": record["provenance"]["qchem_source_input_sha256"],
            "elements": ";".join(molecule["elements"]),
            "spin": molecule["spin"],
            "orbital_qchem_label": record["orbital_basis"]["qchem_rem_label"],
            "orbital_resolution": resolved["orbital_resolution"],
            "orbital_pyscf_name": resolved["orbital_name"],
            "orbital_definition_sha256": orbital_hash,
            "auxiliary_qchem_label": record["auxiliary_basis"]["qchem_rem_label"],
            "auxiliary_resolution": resolved["auxiliary_resolution"],
            "auxiliary_pyscf_name": resolved["auxiliary_name"],
            "auxiliary_definition_sha256": auxiliary_hash,
            "ecp_resolution": resolved["ecp_resolution"],
            "ecp_definition_sha256": ecp_hash,
            "electron_count": orbital_dims["electrons"],
            "ecp_electrons": orbital_dims["ecp_electrons"],
            "orbital_shells": orbital_dims["nbas"],
            "orbital_spherical_aos": orbital_dims["nao"],
            "auxiliary_shells": auxiliary_dims["nbas"],
            "auxiliary_spherical_aos": auxiliary_dims["nao"],
            "runnable_status": "runnable_basis_metadata_validated",
        }
        rows.append(row)
        for key in counters:
            counters[key][str(row[key])] += 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    provenance = {
        "schema_version": 1,
        "status": "built_pending_independent_validation",
        "builder": str(Path(__file__).relative_to(ROOT)),
        "builder_sha256": sha256(Path(__file__)),
        "bridge_module": str(Path(__file__).with_name("pyscf_basis_bridge.py").relative_to(ROOT)),
        "bridge_module_sha256": sha256(Path(__file__).with_name("pyscf_basis_bridge.py")),
        "policy": str(POLICY_PATH.relative_to(ROOT)),
        "policy_sha256": sha256(POLICY_PATH),
        "source_records": str(records_path),
        "source_records_sha256": sha256(records_path),
        "record_count": len(rows),
        "counters": {key: dict(value) for key, value in counters.items()},
        "qchem_auxiliary_sources": {
            name: {"path": str(path), "sha256": sha256(path)}
            for name, path in sorted(QCHEM_AUXILIARY_FILES.items())
        },
        "qchem_orbitals_used": False,
        "qarchive_used": False,
        "outputs": {output_path.name: {"sha256": sha256(output_path), "rows": len(rows)}},
    }
    provenance_path.write_text(json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(provenance, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
