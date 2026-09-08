import pytest
from revwb97m2.scripts.fixed_energy_checkpoint import corrected_fixed


BASE = '''One-Electron Energy = -2536.9603871417
Total Coulomb Energy = 1150.2221758533
Alpha Exchange Energy = -41.0804593049
Beta Exchange Energy = -41.0804593049
SCF energy = -608.98602319
'''


@pytest.mark.parametrize('nuclear', [
    'Nuclear Repulsion Energy = 859.91310676\nNuclear Repu. Energy = 859.9131067110',
    'Nuclear Repu. Energy = 859.9131067110\nNuclear Repulsion Energy = 859.91310676',
    'Nuclear Repu. Energy = 0\nNuclear Repu. Energy = 859.9131067110',
    'Nuclear Repulsion Energy = 859.9131067110',
])
def test_final_breakdown_preference_and_fallback(nuclear):
    result = corrected_fixed(BASE+nuclear, -66.496374449)
    assert result['nuclear_repulsion_hartree'] == 859.9131067110
    assert abs(result['pure_hf_reconstruction_error_hartree']) < 2e-8


def test_missing_nuclear_rejected():
    with pytest.raises(ValueError):
        corrected_fixed(BASE, 0)
