#!/usr/bin/env python3
"""Compare the local paper-precision H2 dissociation fixture with native Q-Chem."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


HARTREE_TO_KCAL_MOL = 627.509474


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def last_float(pattern: str, text: str) -> float:
    matches = re.findall(pattern, text, flags=re.IGNORECASE)
    if not matches:
        raise ValueError(f"Q-Chem fixture lacks pattern: {pattern}")
    return float(matches[-1])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--local-h", type=Path, required=True)
    parser.add_argument("--local-h2", type=Path, required=True)
    parser.add_argument("--qchem-h", type=Path, required=True)
    parser.add_argument("--qchem-h2", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--energy-tolerance", type=float, default=1.0e-7)
    parser.add_argument("--reaction-tolerance-kcal", type=float, default=1.0e-3)
    args = parser.parse_args()

    local_h = json.loads(args.local_h.read_text(encoding="utf-8"))
    local_h2 = json.loads(args.local_h2.read_text(encoding="utf-8"))
    qchem_h_text = args.qchem_h.read_text(encoding="utf-8", errors="replace")
    qchem_h2_text = args.qchem_h2.read_text(encoding="utf-8", errors="replace")

    local_h_energy = float(local_h["energy"]["total_energy_hartree"])
    local_h2_energy = float(local_h2["energy"]["total_energy_hartree"])
    # Native Q-Chem prints the complete one-electron xDH energy before its
    # MP2 driver encounters a zero-pair std::bad_alloc. PT2 is exactly zero.
    qchem_h_energy = last_float(
        r"SCF\s+energy in the final basis set\s*=\s*(-?\d+\.\d+)", qchem_h_text
    )
    qchem_h2_energy = last_float(
        r"RIMP2\s+total energy\s*=\s*(-?\d+\.\d+)", qchem_h2_text
    )
    local_reaction = 2.0 * local_h_energy - local_h2_energy
    qchem_reaction = 2.0 * qchem_h_energy - qchem_h2_energy
    differences = {
        "h_hartree": local_h_energy - qchem_h_energy,
        "h2_hartree": local_h2_energy - qchem_h2_energy,
        "dissociation_hartree": local_reaction - qchem_reaction,
        "dissociation_kcal_mol": (local_reaction - qchem_reaction)
        * HARTREE_TO_KCAL_MOL,
    }
    checks = {
        "local_h_complete": local_h["status"] == "paper_precision_r0_fixture_complete",
        "local_h2_complete": local_h2["status"] == "paper_precision_r0_fixture_complete",
        "h_pt2_exactly_zero": local_h["energy"]["weighted_scalars_hartree"]["pt2"]
        == 0.0,
        "qchem_h_expected_zero_pair_edge_recorded": "std::bad_alloc" in qchem_h_text
        and "wB97M-V orbitals are now ready" in qchem_h_text,
        "qchem_h2_terminal_success": "Thank you very much for using Q-Chem"
        in qchem_h2_text,
        "h_energy_agreement": abs(differences["h_hartree"]) <= args.energy_tolerance,
        "h2_energy_agreement": abs(differences["h2_hartree"])
        <= args.energy_tolerance,
        "reaction_agreement": abs(differences["dissociation_kcal_mol"])
        <= args.reaction_tolerance_kcal,
    }
    report = {
        "schema_version": 1,
        "status": "passed" if all(checks.values()) else "failed",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "reaction": "H2 -> 2 H",
        "checks": checks,
        "energies_hartree": {
            "local_h": local_h_energy,
            "qchem_h": qchem_h_energy,
            "local_h2": local_h2_energy,
            "qchem_h2": qchem_h2_energy,
            "local_dissociation": local_reaction,
            "qchem_dissociation": qchem_reaction,
        },
        "local_minus_qchem": differences,
        "tolerances": {
            "species_hartree": args.energy_tolerance,
            "reaction_kcal_mol": args.reaction_tolerance_kcal,
        },
        "sources": {
            "local_h": {"path": str(args.local_h), "sha256": sha256(args.local_h)},
            "local_h2": {"path": str(args.local_h2), "sha256": sha256(args.local_h2)},
            "qchem_h": {
                "path": str(args.qchem_h),
                "sha256": sha256(args.qchem_h),
                "job_id": 25437044,
                "process_status": "failed_after_complete_pre_pt2_energy",
            },
            "qchem_h2": {
                "path": str(args.qchem_h2),
                "sha256": sha256(args.qchem_h2),
                "job_id": 25437046,
                "process_status": "completed",
            },
        },
    }
    args.output.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
