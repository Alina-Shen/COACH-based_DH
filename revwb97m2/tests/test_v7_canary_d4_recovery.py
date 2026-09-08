import numpy as np
import pytest
from revwb97m2.scripts.recover_v7_canary_d4 import compare_vectors


def test_one_ulp_d4_difference_passes():
    a = np.zeros(292); a[291] = 1.2150854565698372e-6
    b = a.copy(); b[291] = np.nextafter(a[291], np.inf)
    assert compare_vectors(a, b) == b[291]-a[291]
    assert a[291] != b[291]  # Never round/rewrite the saved coefficient.


@pytest.mark.parametrize('index', [0, 64, 288, 289, 290])
def test_non_d4_roundoff_still_fails(index):
    a = np.ones(292); b = a.copy(); b[index] = np.nextafter(a[index], np.inf)
    with pytest.raises(ValueError, match='non-D4'):
        compare_vectors(a, b)


def test_material_d4_change_fails():
    a = np.zeros(292); b = a.copy(); b[291] = 2e-12
    with pytest.raises(ValueError, match='D4 change'):
        compare_vectors(a, b)


@pytest.mark.parametrize('value', [np.inf, np.nan])
def test_nonfinite_d4_fails(value):
    a = np.zeros(292); b = a.copy(); b[291] = value
    with pytest.raises(ValueError, match='nonfinite'):
        compare_vectors(a, b)
