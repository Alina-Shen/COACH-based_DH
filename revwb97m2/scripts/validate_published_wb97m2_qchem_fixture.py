#!/usr/bin/env python3
"""Validate one matched paper-precision R0 result against native Q-Chem."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def last_float(pattern: str, text: str) -> float:
    matches = re.findall(pattern, text, flags=re.IGNORECASE)
    if not matches:
        raise ValueError(f"Q-Chem fixture lacks pattern: {pattern}")
    return float(matches[-1])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--local", type=Path, required=True)
    parser.add_argument("--qchem-output", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--tolerance", type=float, default=1.0e-7)
    args = parser.parse_args()

    local = json.loads(args.local.read_text(encoding="utf-8"))
    qchem_text = args.qchem_output.read_text(encoding="utf-8", errors="replace")
    qchem_parent = last_float(r"\n\s*1[0-9]\s+(-?\d+\.\d+)\s+\S+\s+Convergence criterion met", qchem_text)
    qchem_pre_pt2 = last_float(r"SCF\s+energy in the final basis set\s*=\s*(-?\d+\.\d+)", qchem_text)
    qchem_final = last_float(r"RIMP2\s+total energy\s*=\s*(-?\d+\.\d+)", qchem_text)
    local_parent_manifest = json.loads(
        Path(local["inputs"]["parent_manifest"]).read_text(encoding="utf-8")
    )
    local_parent = float(local_parent_manifest["scf"]["energy_hartree"])
    local_final = float(local["energy"]["total_energy_hartree"])
    local_pt2 = float(local["energy"]["weighted_scalars_hartree"]["pt2"])
    local_pre_pt2 = local_final - local_pt2
    differences = {
        "parent_energy_hartree": local_parent - qchem_parent,
        "pre_pt2_r0_energy_hartree": local_pre_pt2 - qchem_pre_pt2,
        "final_r0_energy_hartree": local_final - qchem_final,
    }
    checks = {
        "local_fixture_complete": local["status"] == "paper_precision_r0_fixture_complete",
        "qchem_terminal_success": "Thank you very much for using Q-Chem" in qchem_text,
        "qchem_native_method": "METHOD wB97M(2)" in qchem_text,
        "qchem_parent_ready": "wB97M-V orbitals are now ready" in qchem_text,
        "qchem_coefficients": all(
            token in qchem_text for token in ("0.62194 SRHF", "0.34096 MP2", "0.65904 VV10(b=10)")
        ),
        "qchem_grid": "(99,590) quadrature" in qchem_text,
        "qchem_one_frozen_core_orbital": "# of frozen core orbitals: 1" in qchem_text,
        "parent_agreement": abs(differences["parent_energy_hartree"]) <= args.tolerance,
        "pre_pt2_agreement": abs(differences["pre_pt2_r0_energy_hartree"]) <= args.tolerance,
        "final_agreement": abs(differences["final_r0_energy_hartree"]) <= args.tolerance,
    }
    report = {
        "schema_version": 1,
        "status": "passed" if all(checks.values()) else "failed",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "tolerance_hartree": args.tolerance,
        "checks": checks,
        "energies_hartree": {
            "local_parent": local_parent,
            "qchem_parent": qchem_parent,
            "local_pre_pt2_r0": local_pre_pt2,
            "qchem_pre_pt2_r0": qchem_pre_pt2,
            "local_final_r0": local_final,
            "qchem_final_r0": qchem_final,
        },
        "local_minus_qchem_hartree": differences,
        "sources": {
            "local_fixture": str(args.local),
            "local_fixture_sha256": sha256(args.local),
            "qchem_output": str(args.qchem_output),
            "qchem_output_sha256": sha256(args.qchem_output),
            "qchem_job_id": 25436961,
        },
    }
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
