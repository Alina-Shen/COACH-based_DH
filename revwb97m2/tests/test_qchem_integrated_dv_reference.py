import numpy as np

from revwb97m2.qchem_integrated_dv_reference import full_integrated_dv_block


def synthetic_inputs():
    return (
        np.array([0.1, 0.2, 0.3, 0.4]),
        np.array([0.8, 0.3, 0.05, 1.1]),
        np.array([0.7, 0.2, 0.02, 0.9]),
        np.array([[0.01, -0.02, 0.03], [0.04, 0.01, -0.02], [0.001, 0.002, -0.001], [-0.03, 0.02, 0.01]]),
        np.array([[-0.02, 0.01, 0.02], [0.03, -0.01, 0.01], [0.002, -0.001, 0.001], [0.02, 0.01, -0.03]]),
        np.array([0.9, 0.4, 0.08, 1.2]),
        np.array([0.8, 0.3, 0.04, 1.0]),
    )


def test_full_reference_shape_finite_and_partition_invariant():
    values = synthetic_inputs()
    full = full_integrated_dv_block(*values)
    split = full_integrated_dv_block(*(value[:2] for value in values))
    split += full_integrated_dv_block(*(value[2:] for value in values))
    assert full.shape == (96, 180)
    assert np.isfinite(full).all()
    np.testing.assert_allclose(full, split, rtol=2.0e-12, atol=2.0e-12)


def test_full_reference_spin_swap_invariant():
    w, ra, rb, ga, gb, ta, tb = synthetic_inputs()
    full = full_integrated_dv_block(w, ra, rb, ga, gb, ta, tb)
    swapped = full_integrated_dv_block(w, rb, ra, gb, ga, tb, ta)
    np.testing.assert_allclose(full, swapped, rtol=2.0e-12, atol=2.0e-12)
