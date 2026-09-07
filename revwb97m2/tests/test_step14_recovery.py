import pytest
from revwb97m2.step14_recovery_v2 import legacy_pt2, scalar_values, fixed_energy

LEGACY = '''Same Spin Scaling factor = 0.34
Opposite Spin Scaling factor = 0.34
TOTAL SS RI-MP2_ENERGY = -0.0298619908
TOTAL OS RI-MP2_ENERGY = -0.0896745535
non-Brillouin singles = 0.0
Total RIMP2 correlation energy = -0.11953654
a_ss = 0.340960
a_os = 0.340960
Thank you very much for using Q-Chem
'''


def test_legacy_uses_precise_factors_and_total_rounding():
    assert legacy_pt2(LEGACY)['total'] == pytest.approx(-0.3505881754458)
    with pytest.raises(ValueError, match='identity failure'):
        legacy_pt2(LEGACY.replace('-0.11953654', '-0.12'))
    with pytest.raises(ValueError, match='unit factors not applied'):
        legacy_pt2(LEGACY, unit_scaled=True)


def test_one_electron_zero_requires_electron_count():
    text = '''Alpha Exchange Energy = -0.2
Beta Exchange Energy = 0.0
Nonlocal correlation = 0.001
There are 1 alpha and 0 beta electrons
Thank you very much for using Q-Chem'''
    assert scalar_values(text, one_electron=True)['pt2_total_hartree'] == 0.
    assert scalar_values(text.replace('Nonlocal correlation', 'DFT Correlation Energy'), one_electron=True)['vv10_hartree'] == .001
    with pytest.raises(ValueError, match='one-electron'):
        scalar_values(text.replace('0 beta', '1 beta'), one_electron=True)


def test_fixed_energy_includes_final_nucleus_field_term():
    text = '''Nuclear Repulsion Energy = 1.0
One-Electron Energy = -10.0
Total Coulomb Energy = 4.0
Alpha Exchange Energy = -1.0
Beta Exchange Energy = -1.0
Nuclear Repu. Energy = 1.001
SCF energy = -6.999
Thank you very much for using Q-Chem'''
    result = fixed_energy(text, -1.5)
    assert result['fixed_energy_hartree'] == pytest.approx(-5.499)
    assert result['pure_hf_reconstruction_error_hartree'] == pytest.approx(0.)
