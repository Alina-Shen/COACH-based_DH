from __future__ import annotations

import numpy as np
from pyscf import dft

from revwb97m2.parent_scf import sg1_prune_all_elements


def test_light_element_branch_matches_pyscf() -> None:
    radial = np.geomspace(1.0e-5, 20.0, 50)
    assert np.array_equal(
        sg1_prune_all_elements(8, radial, 194),
        dft.gen_grid.sg1_prune(8, radial, 194),
    )


def test_published_remaining_element_pattern() -> None:
    radial = np.geomspace(1.0e-5, 20.0, 50)
    angular = sg1_prune_all_elements(79, radial, 194)
    assert np.array_equal(angular[:12], np.full(12, 38))
    assert np.array_equal(angular[12:], np.full(38, 194))
    assert int(angular.sum()) == 7828


def test_heavy_branch_rejects_non_sg1_parent() -> None:
    radial = np.geomspace(1.0e-5, 20.0, 49)
    try:
        sg1_prune_all_elements(79, radial, 194)
    except ValueError as exc:
        assert "requires the published (50,194)" in str(exc)
    else:
        raise AssertionError("heavy-element SG-1 accepted a non-SG-1 parent grid")
