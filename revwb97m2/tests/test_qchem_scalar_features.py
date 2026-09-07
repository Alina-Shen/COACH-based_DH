from __future__ import annotations

import math

import pytest

from revwb97m2.qchem_scalar_features import (
    derive_fixed_energy_input,
    derive_scalar_input,
    derive_pt2_input,
    evaluate_d4_atm_from_qchem_input,
    parse_qchem_fixed_energy_output,
    parse_qchem_scalar_output,
)


SOURCE = """$molecule
0 1
H 0 0 0
$end
$rem
UNRESTRICTED true
AUX_BASIS_CORR rimp2-def2-qzvppd
METHOD = wb97m(os)
DH_PT2_ENGINE rimp2
SCF_GUESS read
$end
"""


def test_derive_scalar_input_freezes_same_archive_controls():
    derived, controls = derive_scalar_input(SOURCE)
    assert "METHOD" not in derived
    assert "DH_PT2_ENGINE" not in derived
    assert "AUX_BASIS" not in derived
    assert "CORRELATION RIMP2" not in derived
    assert controls["MP2_RESTART_NO_SCF"] == "TRUE"
    assert controls["HF_SR"] == "1000"
    assert controls["HF_LR"] == "0"
    assert controls["NL_VV_B"] == "1000"
    assert controls["NL_VV_C"] == "100"
    assert controls["NL_VV_SCALE"] == "100000"


def test_derive_pt2_input_uses_native_double_hybrid_parent_fock():
    derived, controls = derive_pt2_input(SOURCE)
    assert "METHOD wB97M(2)" in derived
    assert "DH_PT2_ENGINE RIMP2" in derived
    assert "AUX_BASIS_CORR rimp2-def2-qzvppd" in derived
    assert controls["MP2_RESTART_NO_SCF"] == "TRUE"


def test_derive_fixed_energy_input_is_pure_full_range_hf():
    derived, controls = derive_fixed_energy_input(SOURCE)
    assert "METHOD" not in derived
    assert "DH_PT2_ENGINE" not in derived
    assert "AUX_BASIS_CORR" not in derived
    assert controls["EXCHANGE"] == "HF"
    assert controls["MAX_SCF_CYCLES"] == "0"
    assert "HF_SR" not in derived and "HF_LR" not in derived


def test_parser_combines_spins_and_checks_mp2_components():
    output = """
 Alpha Exchange Energy = -3.0000000000
 Beta  Exchange  Energy = -2.0000000000
 Nonlocal correlation = 0.0200000000
 total same-spin energy = -0.1000000000
 total opposite-spin energy = -0.2000000000
 Same Spin Scaling factor = 0.500000
 Opposite Spin Scaling factor = 0.500000
 non-Brillouin singles = -0.0100000000
 PT2 Correlation Energy (scE_PT2c) = -0.3000000000
 Reading MOs from coefficient file
 Reading MOs from coefficient file
 Thank you very much for using Q-Chem
 """
    parsed = parse_qchem_scalar_output(output)
    assert parsed["short_range_hf_hartree"] == pytest.approx(-5.0)
    assert parsed["vv10_hartree"] == pytest.approx(0.02)
    assert parsed["pt2_total_hartree"] == pytest.approx(-0.6)
    assert parsed["pt2_same_spin_hartree"] == pytest.approx(-0.2)
    assert parsed["pt2_opposite_spin_hartree"] == pytest.approx(-0.4)
    assert parsed["pt2_non_brillouin_singles_excluded_hartree"] == pytest.approx(-0.01)
    assert parsed["pt2_component_sum_error_hartree"] == pytest.approx(0.0)
    assert parsed["pt2_scaled_identity_error_hartree"] == pytest.approx(0.0)
    assert parsed["normal_qchem_termination"] is True


def test_d4_from_qchem_input_is_geometry_only_and_finite():
    water = """$molecule
0 1
O 0.0 0.0 0.0
H 0.0 0.0 0.96
H 0.0 0.90 -0.24
$end
$rem
METHOD hf
$end
"""
    energy = evaluate_d4_atm_from_qchem_input(water)
    assert math.isfinite(energy)
    assert energy == pytest.approx(1.2598572504082371e-11)


def test_fixed_energy_parser_uses_full_hf_minus_short_range_hf():
    output = """
 One-Electron Energy = -10.0000000000
 Total Coulomb Energy = 4.0000000000
 Alpha Exchange Energy = -1.5000000000
 Beta Exchange Energy = -1.5000000000
 Nuclear Repu. Energy = 2.0000000000
 SCF energy = -7.0000000000
 Reading MOs from coefficient file
 Reading MOs from coefficient file
 Thank you very much for using Q-Chem
 """
    parsed = parse_qchem_fixed_energy_output(output, -2.5)
    assert parsed["full_hf_exchange_hartree"] == pytest.approx(-3.0)
    assert parsed["full_long_range_hf_exchange_hartree"] == pytest.approx(-0.5)
    assert parsed["fixed_energy_hartree"] == pytest.approx(-4.5)
    assert parsed["pure_hf_reconstruction_error_hartree"] == pytest.approx(0.0)
