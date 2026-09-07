"""Q-Chem imported-orbital scalar features for revwb97m2 Step 9.

The production route evaluates SR-HF/VV10 and frozen-core RI-MP2 in two
fixed-orbital Q-Chem jobs that read the same copied archive. D4-ATM remains a
geometry-only post-processing term. This module contains the input transforms
and strict output parser; it does not run Q-Chem or mutate an authoritative
orbital directory.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any

import numpy as np


FLOAT = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[EeDd][-+]?\d+)?"
BOHR_ANGSTROM = 0.529177210903
D4_PARAMETERS = {"s6": 0.0, "s8": 0.0, "s9": 1.0, "a1": 0.215, "a2": 5.8, "alp": 16.0}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def tree_manifest(root: Path) -> list[dict[str, object]]:
    return [
        {
            "path": str(path.relative_to(root)),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        for path in sorted(root.rglob("*"))
        if path.is_file()
    ]


def _set_rem(rem: str, key: str, value: str) -> str:
    pattern = re.compile(rf"(?im)^\s*{re.escape(key)}\s*(?:=\s*)?\S+\s*$")
    matches = pattern.findall(rem)
    if len(matches) > 1:
        raise ValueError(f"expected at most one {key}, found {len(matches)}")
    if matches:
        return pattern.sub(f"{key} {value}", rem)
    end = re.search(r"(?im)^\s*\$end\s*$", rem)
    if end is None:
        raise ValueError("$rem block has no $end")
    return rem[: end.start()] + f"{key} {value}\n" + rem[end.start() :]


def _remove_rem(rem: str, key: str) -> str:
    return re.sub(rf"(?im)^\s*{re.escape(key)}\s*(?:=\s*)?\S+\s*\n?", "", rem)


def _read_rem_value(rem: str, key: str) -> str:
    matches = re.findall(rf"(?im)^\s*{re.escape(key)}\s*(?:=\s*)?(\S+)\s*$", rem)
    if len(matches) != 1:
        raise ValueError(f"expected exactly one {key}, found {len(matches)}")
    return matches[0]


def derive_scalar_input(source: str, *, settings=None) -> tuple[str, dict[str, str]]:
    """Derive the fixed-orbital SR-HF/VV10 input.

    Q-Chem's SRC route constructs separate erf/erfc exchange matrices.  With
    HF_SR=1 and HF_LR=0, the printed alpha+beta exchange is the unscaled
    erfc(omega*r12)/r12 HF exchange requested by the COACH model.
    """

    match = re.search(r"(?ims)^\s*\$rem\s*$.*?^\s*\$end\s*$", source)
    if match is None:
        raise ValueError("authoritative input has no complete $rem block")
    rem = match.group(0)
    _read_rem_value(rem, "AUX_BASIS_CORR")
    for key in ("METHOD", "DH_PT2_ENGINE", "AUX_BASIS_CORR", "CORRELATION", "AUX_BASIS"):
        rem = _remove_rem(rem, key)
    controls = {
        "JOBTYPE": "SP",
        "EXCHANGE": "HF",
        "UNRESTRICTED": "TRUE",
        "SCF_GUESS": "READ",
        "MAX_SCF_CYCLES": "0",
        "MP2_RESTART_NO_SCF": "TRUE",
        "GEN_SCFMAN": "FALSE",
        "SCF_FINAL_PRINT": "1",
        "LRC_DFT": "TRUE",
        "SRC_DFT": "TRUE",
        "OMEGA": "300",
        "OMEGA2": "300",
        "HF_SR": "1000",
        "HF_LR": "0",
        "NL_CORRELATION": "VV10",
        "NL_GRID": "1",
        "NL_VV_B": "1000",
        "NL_VV_C": "100",
        "NL_VV_SCALE": "100000",
    }
    if settings is not None:
        # Explicit v7 caller only. Historical Step9/13 contracts remain b=10.
        if (settings.vv10_b, settings.vv10_c) != (5.5, 0.01):
            raise ValueError('unsupported v7 VV10 definition')
        controls['NL_VV_B'] = '550'
    for key, value in controls.items():
        rem = _set_rem(rem, key, value)
    derived = source[: match.start()] + rem + source[match.end() :]
    return derived, controls


def derive_pt2_input(source: str) -> tuple[str, dict[str, str]]:
    """Derive the fixed-WB97M-V-orbital native double-hybrid RI-MP2 input."""

    match = re.search(r"(?ims)^\s*\$rem\s*$.*?^\s*\$end\s*$", source)
    if match is None:
        raise ValueError("authoritative input has no complete $rem block")
    rem = match.group(0)
    controls = {
        "JOBTYPE": "SP",
        "METHOD": "wB97M(2)",
        "DH_PT2_ENGINE": "RIMP2",
        "N_FROZEN_CORE": "FC",
        "UNRESTRICTED": "TRUE",
        "SCF_GUESS": "READ",
        "MAX_SCF_CYCLES": "0",
        "MP2_RESTART_NO_SCF": "TRUE",
        "GEN_SCFMAN": "FALSE",
        "SCF_FINAL_PRINT": "1",
    }
    for key, value in controls.items():
        rem = _set_rem(rem, key, value)
    return source[: match.start()] + rem + source[match.end() :], controls


def derive_fixed_energy_input(source: str) -> tuple[str, dict[str, str]]:
    """Derive a pure full-range HF component-print job on fixed orbitals."""

    match = re.search(r"(?ims)^\s*\$rem\s*$.*?^\s*\$end\s*$", source)
    if match is None:
        raise ValueError("authoritative input has no complete $rem block")
    rem = match.group(0)
    for key in (
        "METHOD", "DH_PT2_ENGINE", "AUX_BASIS_CORR", "CORRELATION", "AUX_BASIS",
        "LRC_DFT", "SRC_DFT", "OMEGA", "OMEGA2", "HF_SR", "HF_LR",
        "NL_CORRELATION", "NL_GRID", "NL_VV_B", "NL_VV_C", "NL_VV_SCALE",
    ):
        rem = _remove_rem(rem, key)
    controls = {
        "JOBTYPE": "SP",
        "EXCHANGE": "HF",
        "UNRESTRICTED": "TRUE",
        "SCF_GUESS": "READ",
        "MAX_SCF_CYCLES": "0",
        "MP2_RESTART_NO_SCF": "TRUE",
        "GEN_SCFMAN": "FALSE",
        "SCF_FINAL_PRINT": "1",
    }
    for key, value in controls.items():
        rem = _set_rem(rem, key, value)
    return source[: match.start()] + rem + source[match.end() :], controls


def _last_float(text: str, patterns: tuple[str, ...], label: str) -> float:
    values: list[float] = []
    for pattern in patterns:
        values.extend(float(value.replace("D", "E").replace("d", "e")) for value in re.findall(pattern, text, re.I))
    if not values:
        raise ValueError(f"Q-Chem output has no {label}")
    return values[-1]


def parse_qchem_scalar_output(text: str, pt2_text: str | None = None) -> dict[str, Any]:
    """Parse raw SR-HF/VV10 and canonical RI-MP2 doubles diagnostics."""

    alpha = _last_float(text, (rf"Alpha\s+Exchange\s+Energy\s*=\s*({FLOAT})",), "alpha exchange")
    beta = _last_float(text, (rf"Beta\s+Exchange\s+Energy\s*=\s*({FLOAT})",), "beta exchange")
    vv10 = _last_float(
        text,
        (
            rf"Nonlocal\s+correlation\s*=\s*({FLOAT})",
            rf"DFT\s+Correlation\s+Energy\s*=\s*({FLOAT})",
        ),
        "VV10 energy",
    )
    if pt2_text is None:
        pt2_text = text
    scaled_same_spin = _last_float(
        pt2_text,
        (rf"(?:total\s+)?same[- ]spin\s+(?:RI-?)?MP2?\s*(?:correlation\s+)?energy\s*=\s*({FLOAT})", rf"total\s+same-spin\s+energy\s*=\s*({FLOAT})"),
        "RI-MP2 same-spin correlation",
    )
    scaled_opposite_spin = _last_float(
        pt2_text,
        (rf"(?:total\s+)?opposite[- ]spin\s+(?:RI-?)?MP2?\s*(?:correlation\s+)?energy\s*=\s*({FLOAT})", rf"total\s+opposite-spin\s+energy\s*=\s*({FLOAT})"),
        "RI-MP2 opposite-spin correlation",
    )
    same_spin_scale = _last_float(
        pt2_text,
        (rf"Same\s+Spin\s+Scaling\s+factor\s*=\s*({FLOAT})",),
        "same-spin RI-MP2 scale",
    )
    opposite_spin_scale = _last_float(
        pt2_text,
        (rf"Opposite\s+Spin\s+Scaling\s+factor\s*=\s*({FLOAT})",),
        "opposite-spin RI-MP2 scale",
    )
    if same_spin_scale == 0.0 or opposite_spin_scale == 0.0:
        raise ValueError("native double-hybrid RI-MP2 diagnostic scale is zero")
    same_spin = scaled_same_spin / same_spin_scale
    opposite_spin = scaled_opposite_spin / opposite_spin_scale
    total = same_spin + opposite_spin
    scaled_total = _last_float(
        pt2_text,
        (rf"PT2\s+Correlation\s+Energy\s+\(scE_PT2c\)\s*=\s*({FLOAT})",),
        "scaled double-hybrid RI-MP2 correlation",
    )
    singles = _last_float(
        pt2_text,
        (rf"non-Brillouin\s+singles\s*=\s*({FLOAT})",),
        "non-Brillouin singles",
    )
    result = {
        "short_range_hf_hartree": alpha + beta,
        "short_range_hf_alpha_hartree": alpha,
        "short_range_hf_beta_hartree": beta,
        "vv10_hartree": vv10,
        "pt2_total_hartree": total,
        "pt2_same_spin_hartree": same_spin,
        "pt2_opposite_spin_hartree": opposite_spin,
        "pt2_component_sum_error_hartree": total - same_spin - opposite_spin,
        "pt2_same_spin_scale": same_spin_scale,
        "pt2_opposite_spin_scale": opposite_spin_scale,
        "pt2_non_brillouin_singles_excluded_hartree": singles,
        "pt2_scaled_reported_total_hartree": scaled_total,
        "pt2_scaled_identity_error_hartree": scaled_total - scaled_same_spin - scaled_opposite_spin,
        "normal_qchem_termination": "Thank you very much for using Q-Chem" in text and "Thank you very much for using Q-Chem" in pt2_text,
        "archive_read_count": text.count("Reading MOs from coefficient file") + pt2_text.count("Reading MOs from coefficient file"),
    }
    if not np.isfinite(list(value for value in result.values() if isinstance(value, float))).all():
        raise FloatingPointError("Q-Chem scalar output contains non-finite values")
    return result


def parse_qchem_fixed_energy_output(text: str, short_range_hf_hartree: float) -> dict[str, float | bool]:
    """Recover the coefficient-independent partition from a pure-HF printout.

    Full-range HF exchange is the exact sum of its erfc short-range and erf
    long-range pieces at the same omega.  Step 9 supplies the former; this
    pure-HF fixed-orbital job supplies their sum.
    """

    one_electron = _last_float(text, (rf"One-Electron\s+Energy\s*=\s*({FLOAT})",), "one-electron energy")
    coulomb = _last_float(text, (rf"Total\s+Coulomb\s+Energy\s*=\s*({FLOAT})",), "Coulomb energy")
    alpha = _last_float(text, (rf"Alpha\s+Exchange\s+Energy\s*=\s*({FLOAT})",), "alpha exchange")
    beta = _last_float(text, (rf"Beta\s+Exchange\s+Energy\s*=\s*({FLOAT})",), "beta exchange")
    nuclear = _last_float(text, (rf"Nuclear\s+Repu\.\s+Energy\s*=\s*({FLOAT})", rf"Nuclear\s+Repulsion\s+Energy\s*=\s*({FLOAT})"), "nuclear repulsion")
    reported = _last_float(text, (rf"SCF\s+energy\s*=\s*({FLOAT})",), "SCF energy")
    full_hf = alpha + beta
    long_range_hf = full_hf - float(short_range_hf_hartree)
    pure_hf_reconstructed = nuclear + one_electron + coulomb + full_hf
    fixed = nuclear + one_electron + coulomb + long_range_hf
    result: dict[str, float | bool] = {
        "nuclear_repulsion_hartree": nuclear,
        "one_electron_hartree": one_electron,
        "coulomb_hartree": coulomb,
        "full_hf_exchange_hartree": full_hf,
        "short_range_hf_hartree": float(short_range_hf_hartree),
        "full_long_range_hf_exchange_hartree": long_range_hf,
        "fixed_energy_hartree": fixed,
        "pure_hf_reported_energy_hartree": reported,
        "pure_hf_reconstruction_error_hartree": pure_hf_reconstructed - reported,
        "normal_qchem_termination": "Thank you very much for using Q-Chem" in text,
        "archive_read_count": text.count("Reading MOs from coefficient file"),
    }
    numeric = [value for value in result.values() if isinstance(value, float)]
    if not np.isfinite(numeric).all():
        raise FloatingPointError("Q-Chem fixed-energy output contains non-finite values")
    return result


def evaluate_d4_atm_from_qchem_input(source: str) -> float:
    """Evaluate the frozen geometry-only COACH D4-ATM feature."""

    from dftd4.interface import DampingParam, DispersionModel
    from pyscf.data import elements

    match = re.search(r"(?ims)^\s*\$molecule\s*$\s*(.*?)^\s*\$end\s*$", source)
    if match is None:
        raise ValueError("Q-Chem input has no complete $molecule block")
    lines = [line.strip() for line in match.group(1).splitlines() if line.strip()]
    charge_fields = lines[0].split()
    if len(charge_fields) != 2:
        raise ValueError("Q-Chem molecule must begin with charge and multiplicity")
    charge = int(charge_fields[0])
    numbers: list[int] = []
    positions: list[list[float]] = []
    for line in lines[1:]:
        fields = line.split()
        if len(fields) != 4 or fields[0].startswith("@"):  # Ghost centers are not supported here.
            raise ValueError(f"D4 gateway requires real Cartesian atoms: {line}")
        numbers.append(elements.charge(fields[0]))
        positions.append([float(value) / BOHR_ANGSTROM for value in fields[1:]])
    model = DispersionModel(
        numbers=np.asarray(numbers, dtype=int),
        positions=np.asarray(positions, dtype=float),
        charge=float(charge),
    )
    energy = float(model.get_dispersion(DampingParam(**D4_PARAMETERS), grad=False)["energy"])
    if not np.isfinite(energy):
        raise FloatingPointError("non-finite D4-ATM energy")
    return energy


def publish_scalar_case(case_root: Path, d4_atm_hartree: float | None = None) -> dict[str, Any]:
    """Validate provenance and atomically publish one four-scalar artifact."""

    case_root = case_root.resolve()
    prepared_path = case_root / "PREPARED.json"
    output_path = case_root / "qchem.out"
    pt2_output_path = case_root / "qchem.pt2.out"
    prepared = json.loads(prepared_path.read_text(encoding="utf-8"))
    parsed = parse_qchem_scalar_output(
        output_path.read_text(encoding="utf-8", errors="replace"),
        pt2_output_path.read_text(encoding="utf-8", errors="replace"),
    )
    source_input_text = Path(prepared["authoritative_input"]).read_text(encoding="utf-8")
    evaluated_d4 = evaluate_d4_atm_from_qchem_input(source_input_text)
    if d4_atm_hartree is not None and abs(evaluated_d4 - d4_atm_hartree) > 1.0e-12:
        raise ValueError("provided D4-ATM value differs from direct frozen-definition evaluation")
    d4_atm_hartree = evaluated_d4
    copied = case_root / "qcscratch" / "step9_scalar"
    source = Path(prepared["source_orbital_root"])
    source_tree = tree_manifest(source)
    copied_tree = tree_manifest(copied)
    source_qarchive_hash = sha256(source / "qarchive.h5")
    copied_qarchive_hash = sha256(copied / "qarchive.h5")
    checks = {
        "source_tree_unchanged": source_tree == prepared["source_tree"],
        "pre_run_source_copy_identity": prepared["source_tree"] == prepared["copy_tree"],
        "post_run_qarchive_identity": source_qarchive_hash == copied_qarchive_hash,
        "normal_qchem_termination": parsed["normal_qchem_termination"],
        "archive_read": parsed["archive_read_count"] >= 4,
        "pt2_component_sum": abs(parsed["pt2_component_sum_error_hartree"]) <= 1.0e-10,
        "pt2_scaled_identity": abs(parsed["pt2_scaled_identity_error_hartree"]) <= 2.0e-10,
    }
    if not all(checks.values()):
        raise RuntimeError(f"Step 9 scalar validation failed: {[key for key, value in checks.items() if not value]}")
    scalars = np.asarray(
        [parsed["short_range_hf_hartree"], parsed["vv10_hartree"], parsed["pt2_total_hartree"], d4_atm_hartree],
        dtype=np.float64,
    )
    artifact = case_root / "published"
    if artifact.exists():
        raise FileExistsError(f"refusing to overwrite {artifact}")
    temporary = case_root / f".published.tmp.{os.getpid()}"
    temporary.mkdir()
    np.save(temporary / "scalar_features_288_291.npy", scalars)
    report = {
        "schema_version": 2,
        "status": "qchem_same_archive_scalar_features_complete_and_validated",
        "species": prepared["species"],
        "feature_indices": [288, 289, 290, 291],
        "values_hartree": {**parsed, "d4_atm_hartree": float(d4_atm_hartree)},
        "checks": checks,
        "source": {
            "authoritative_input": prepared["authoritative_input"],
            "authoritative_input_sha256": prepared["authoritative_input_sha256"],
            "source_orbital_root": str(source),
            "qarchive_sha256": source_qarchive_hash,
            "copied_qarchive_sha256": copied_qarchive_hash,
            "post_run_scratch_tree_changed_as_expected": copied_tree != prepared["copy_tree"],
            "derived_input_sha256": sha256(case_root / "input.step9.in"),
            "qchem_output_sha256": sha256(output_path),
            "qchem_pt2_output_sha256": sha256(pt2_output_path),
        },
    }
    (temporary / "scalar_manifest.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (temporary / "SCALAR_COMPLETE").write_text("complete\n", encoding="utf-8")
    temporary.rename(artifact)
    return report
