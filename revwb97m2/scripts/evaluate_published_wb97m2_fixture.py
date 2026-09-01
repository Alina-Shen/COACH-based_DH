#!/usr/bin/env python3
"""Evaluate paper-precision published omegaB97M(2) from a validated checkpoint."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
from pyscf import dft


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from revwb97m2 import integrated_dv  # noqa: E402
from revwb97m2 import published_wb97m2 as r0  # noqa: E402
from revwb97m2.parent_scf import (  # noqa: E402
    DEFAULT_SPEC,
    load_bridge_row,
    load_checkpoint_parent,
    load_record,
    load_spec,
    input_artifact_paths,
    sha256,
    spin_density_matrices,
    utc_now,
    validate_published_parent,
    validate_record,
)
from revwb97m2.scripts.pyscf_basis_bridge import build_molecules  # noqa: E402


def evaluate_grid(
    mol: object,
    dm_a: np.ndarray,
    dm_b: np.ndarray,
    radial: int,
    angular: int,
    block_size: int,
) -> tuple[dict[str, float], int, str]:
    coords, weights, grid_id = integrated_dv.build_grid(mol, radial, angular)
    components = {name: 0.0 for name in r0.SEMILOCAL_COEFFICIENTS}
    numint = dft.numint.NumInt()
    for start in range(0, weights.size, block_size):
        stop = min(start + block_size, weights.size)
        ao = numint.eval_ao(mol, coords[start:stop], deriv=1)
        rho_a_mgga = numint.eval_rho(mol, ao, dm_a, xctype="MGGA", with_lapl=False)
        rho_b_mgga = numint.eval_rho(mol, ao, dm_b, xctype="MGGA", with_lapl=False)
        rho_a, grad_a, tau_a = integrated_dv.unpack_mgga_rho(rho_a_mgga)
        rho_b, grad_b, tau_b = integrated_dv.unpack_mgga_rho(rho_b_mgga)
        block = r0.published_semilocal_components_block(
            weights[start:stop], rho_a, rho_b, grad_a, grad_b, tau_a, tau_b
        )
        for name, value in block.items():
            components[name] += value
    return components, int(weights.size), grid_id


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--species", required=True)
    parser.add_argument("--parent-dir", type=Path, required=True)
    parser.add_argument("--scalar-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    parser.add_argument("--radial", type=int, default=99)
    parser.add_argument("--angular", type=int, default=590)
    parser.add_argument("--block-size", type=int, default=10000)
    parser.add_argument("--max-memory-mb", type=int, default=40000)
    args = parser.parse_args()

    started = time.perf_counter()
    spec = load_spec(args.spec)
    checks, _ = validate_published_parent(args.parent_dir, args.spec)
    if not all(checks.values()):
        raise ValueError(f"parent validation failed: {[name for name, ok in checks.items() if not ok]}")
    parent_manifest_path = args.parent_dir / "parent_manifest.json"
    parent_manifest = json.loads(parent_manifest_path.read_text(encoding="utf-8"))
    scalar_manifest_path = args.scalar_dir / "scalar_manifest.json"
    scalar_manifest = json.loads(scalar_manifest_path.read_text(encoding="utf-8"))
    if parent_manifest["species"] != args.species or scalar_manifest["species"] != args.species:
        raise ValueError("fixture species does not match parent/scalar artifacts")
    if scalar_manifest["parent"]["checkpoint_sha256"] != parent_manifest["artifacts_sha256"][
        spec["orbital_source"]["checkpoint_name"]
    ]:
        raise ValueError("scalar artifact does not reference the selected parent checkpoint")

    record, line_number = load_record(input_artifact_paths(spec)["records"], args.species)
    bridge_row = load_bridge_row(spec, args.species)
    validate_record(record, bridge_row)
    mol, _, _ = build_molecules(record)
    checkpoint = args.parent_dir / spec["orbital_source"]["checkpoint_name"]
    mf = load_checkpoint_parent(checkpoint, mol, record, spec, args.max_memory_mb)
    dm_a, dm_b = spin_density_matrices(mf)
    semilocal, point_count, grid_id = evaluate_grid(
        mol, dm_a, dm_b, args.radial, args.angular, args.block_size
    )
    scalar = scalar_manifest["scalar_features"]
    components = {
        **scalar_manifest["fixed_energy"],
        **semilocal,
        "short_range_hf": scalar["short_range_hf"]["energy_hartree"],
        "vv10": scalar["vv10"]["energy_hartree"],
        "pt2": scalar["pt2"]["total_correlation_hartree"],
    }
    components.pop("total_hartree")
    energy = r0.evaluate_r0_components(components)
    report = {
        "schema_version": 1,
        "status": "paper_precision_r0_fixture_complete",
        "created_utc": utc_now(),
        "species": args.species,
        "immutable_record_line": line_number,
        "coefficient_authority": "omegaB97M(2)_Table_II_five_decimal_printed_precision",
        "semilocal_authority": "omegaB97M-V_Section_V_and_uploaded_SI_source",
        "reference": parent_manifest["reference"],
        "grid": {"id": grid_id, "radial": args.radial, "angular": args.angular, "points": point_count},
        "components_hartree": components,
        "energy": energy,
        "inputs": {
            "parent_manifest": str(parent_manifest_path),
            "parent_manifest_sha256": sha256(parent_manifest_path),
            "checkpoint_sha256": sha256(checkpoint),
            "scalar_manifest": str(scalar_manifest_path),
            "scalar_manifest_sha256": sha256(scalar_manifest_path),
        },
        "qchem_orbitals_used": False,
        "elapsed_seconds": time.perf_counter() - started,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
