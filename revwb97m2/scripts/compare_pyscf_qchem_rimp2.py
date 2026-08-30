#!/usr/bin/env python3
"""Compare PySCF RI-MP2 with Q-Chem RIMP2 and conventional MP2.

The Q-Chem wB97M(OS) output reports an opposite-spin RIMP2 contribution after
applying ``a_os``.  This script reconstructs the unscaled Q-Chem OS value,
runs a matching unrestricted PySCF omegaB97M-V parent calculation, and checks
both density-fitted and conventional UMP2 on the fixed PySCF orbitals.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pyscf
from pyscf import dft, gto, mp
from pyscf.data import elements


FLOAT = r"[-+]?\d+(?:\.\d*)?(?:[EeDd][-+]?\d+)?"
HARTREE_TO_KCAL_PER_MOL = 627.50947406
COACH_NUMERICAL_THRESHOLD_KCAL_PER_MOL = 0.015


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--qchem-input", type=Path, required=True)
    parser.add_argument("--qchem-output", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--reuse-calculation",
        type=Path,
        help="Reuse qchem/pyscf/job values from an existing report instead of recalculating",
    )
    parser.add_argument("--max-memory-mb", type=int, default=8000)
    parser.add_argument("--verbose", type=int, default=4)
    parser.add_argument("--parent-tolerance-hartree", type=float, default=2.0e-6)
    parser.add_argument("--cross-engine-os-tolerance-hartree", type=float, default=5.0e-6)
    parser.add_argument(
        "--ri-reference-tolerance-hartree",
        type=float,
        default=COACH_NUMERICAL_THRESHOLD_KCAL_PER_MOL / HARTREE_TO_KCAL_PER_MOL,
    )
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def as_float(value: str) -> float:
    return float(value.replace("D", "E").replace("d", "e"))


def parse_qchem_input(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    molecule_match = re.search(r"\$molecule\s*(.*?)\s*\$end", text, re.I | re.S)
    rem_match = re.search(r"\$rem\s*(.*?)\s*\$end", text, re.I | re.S)
    if molecule_match is None or rem_match is None:
        raise ValueError("Q-Chem input must contain $molecule and $rem sections")

    molecule_lines = [line.strip() for line in molecule_match.group(1).splitlines() if line.strip()]
    charge, multiplicity = (int(value) for value in molecule_lines[0].split()[:2])
    atom = "\n".join(molecule_lines[1:])

    rem = {}
    for line in rem_match.group(1).splitlines():
        fields = line.split()
        if len(fields) >= 2:
            rem[fields[0].upper()] = fields[-1]
    grid = rem["XC_GRID"].zfill(12)
    return {
        "atom": atom,
        "charge": charge,
        "multiplicity": multiplicity,
        "spin": multiplicity - 1,
        "basis": rem["BASIS"],
        "auxiliary_basis_qchem": rem["AUX_BASIS_CORR"],
        "auxiliary_basis_pyscf": rem["AUX_BASIS_CORR"].lower().removeprefix("rimp2-") + "-ri",
        "xc_grid": {"radial": int(grid[:6]), "angular": int(grid[6:])},
        "unrestricted": rem.get("UNRESTRICTED", "FALSE").upper() == "TRUE",
        "frozen_core": rem.get("N_FROZEN_CORE", "").upper() == "FC",
    }


def last_match(pattern: str, text: str, label: str) -> float:
    matches = re.findall(pattern, text, re.I | re.M)
    if not matches:
        raise ValueError(f"Could not parse {label} from Q-Chem output")
    value = matches[-1]
    if isinstance(value, tuple):
        value = value[-1]
    return as_float(value)


def parse_qchem_output(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    if "Thank you very much for using Q-Chem" not in text:
        raise ValueError("Q-Chem output has no successful completion footer")
    parent = last_match(rf"^\s*\d+\s+({FLOAT})\s+{FLOAT}\s+Convergence criterion met", text, "parent energy")
    scaled_os = last_match(rf"total opposite-spin energy\s*=\s*({FLOAT})", text, "scaled OS RIMP2")
    a_os = last_match(rf"^\s*a_os\s*=\s*({FLOAT})", text, "a_os")
    if a_os == 0.0:
        raise ValueError("Q-Chem a_os is zero; cannot reconstruct unscaled OS energy")
    return {
        "parent_energy_hartree": parent,
        "scaled_opposite_spin_rimp2_hartree": scaled_os,
        "opposite_spin_scale": a_os,
        "unscaled_opposite_spin_rimp2_hartree": scaled_os / a_os,
    }


def mp2_result(calculation) -> dict:
    correlation, _ = calculation.kernel()
    return {
        "correlation_energy_hartree": float(correlation),
        "same_spin_energy_hartree": float(calculation.e_corr_ss),
        "opposite_spin_energy_hartree": float(calculation.e_corr_os),
    }


def main() -> int:
    args = parse_args()
    qchem_input = args.qchem_input.resolve()
    qchem_output = args.qchem_output.resolve()
    output = args.output.resolve()
    job = parse_qchem_input(qchem_input)
    qchem = parse_qchem_output(qchem_output)
    if not job["unrestricted"]:
        raise ValueError("Comparison fixture must use the Q-Chem unrestricted reference")

    reuse_provenance = None
    if args.reuse_calculation is not None:
        reuse_path = args.reuse_calculation.resolve()
        reused = json.loads(reuse_path.read_text(encoding="utf-8"))
        if reused["job"] != job or reused["qchem"] != qchem:
            raise ValueError("Reused calculation does not match the supplied Q-Chem fixture")
        parent_energy = float(reused["pyscf"]["parent_energy_hartree"])
        frozen = int(reused["pyscf"]["frozen_core_orbitals"])
        conventional = reused["pyscf"]["conventional_ump2_reference"]
        density_fitted = reused["pyscf"]["density_fitted_ump2"]
        reuse_provenance = {"path": str(reuse_path), "sha256": sha256(reuse_path)}
    else:
        mol = gto.M(
            atom=job["atom"],
            basis=job["basis"],
            charge=job["charge"],
            spin=job["spin"],
            unit="Angstrom",
            max_memory=args.max_memory_mb,
            verbose=args.verbose,
        )
        mf = dft.UKS(mol)
        mf.xc = "wb97m-v"
        mf.conv_tol = 1.0e-9
        mf.max_cycle = 200
        mf.max_memory = args.max_memory_mb
        mf.grids.atom_grid = (job["xc_grid"]["radial"], job["xc_grid"]["angular"])
        mf.grids.prune = None
        mf.grids.radii_adjust = None
        mf.nlcgrids.atom_grid = (50, 194)
        mf.nlcgrids.prune = dft.gen_grid.sg1_prune
        mf.nlcgrids.radii_adjust = None
        parent_energy = float(mf.kernel())
        if not mf.converged:
            raise RuntimeError("PySCF omegaB97M-V parent SCF did not converge")

        frozen = int(elements.chemcore(mol)) if job["frozen_core"] else 0
        conventional = mp2_result(mp.UMP2(mf, frozen=frozen))
        density_fitted = mp2_result(
            mp.UMP2(mf, frozen=frozen).density_fit(auxbasis=job["auxiliary_basis_pyscf"])
        )

    differences = {
        "parent_pyscf_minus_qchem_hartree": parent_energy - qchem["parent_energy_hartree"],
        "scaled_os_pyscf_minus_qchem_hartree": (
            density_fitted["opposite_spin_energy_hartree"] * qchem["opposite_spin_scale"]
            - qchem["scaled_opposite_spin_rimp2_hartree"]
        ),
        "ri_minus_conventional_total_hartree": (
            density_fitted["correlation_energy_hartree"]
            - conventional["correlation_energy_hartree"]
        ),
        "ri_minus_conventional_same_spin_hartree": (
            density_fitted["same_spin_energy_hartree"]
            - conventional["same_spin_energy_hartree"]
        ),
        "ri_minus_conventional_opposite_spin_hartree": (
            density_fitted["opposite_spin_energy_hartree"]
            - conventional["opposite_spin_energy_hartree"]
        ),
    }
    checks = {
        "parent_matches_qchem": abs(differences["parent_pyscf_minus_qchem_hartree"])
        <= args.parent_tolerance_hartree,
        "scaled_os_matches_qchem": abs(differences["scaled_os_pyscf_minus_qchem_hartree"])
        <= args.cross_engine_os_tolerance_hartree,
        "ri_total_matches_conventional": abs(differences["ri_minus_conventional_total_hartree"])
        <= args.ri_reference_tolerance_hartree,
        "ri_spin_components_sum": abs(
            density_fitted["correlation_energy_hartree"]
            - density_fitted["same_spin_energy_hartree"]
            - density_fitted["opposite_spin_energy_hartree"]
        )
        <= 1.0e-12,
    }
    report = {
        "schema_version": 1,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "passed": all(checks.values()),
        "checks": checks,
        "tolerances_hartree": {
            "parent_cross_engine": args.parent_tolerance_hartree,
            "scaled_os_cross_engine": args.cross_engine_os_tolerance_hartree,
            "ri_vs_conventional": args.ri_reference_tolerance_hartree,
        },
        "tolerance_basis": {
            "ri_vs_conventional": (
                "COACH numerical-stability threshold: 0.015 kcal/mol converted to hartree"
            ),
            "spin_components": "diagnostic only; the fitted feature is total PT2 correlation",
        },
        "job": job,
        "qchem": qchem,
        "pyscf": {
            "parent_energy_hartree": parent_energy,
            "frozen_core_orbitals": frozen,
            "density_fitted_ump2": density_fitted,
            "conventional_ump2_reference": conventional,
        },
        "differences": differences,
        "provenance": {
            "qchem_input": str(qchem_input),
            "qchem_input_sha256": sha256(qchem_input),
            "qchem_output": str(qchem_output),
            "qchem_output_sha256": sha256(qchem_output),
            "python_version": platform.python_version(),
            "pyscf_version": pyscf.__version__,
            "numpy_version": np.__version__,
            "reused_calculation_report": reuse_provenance,
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
