from __future__ import annotations

import numpy as np

from revwb97m2.semilocal_features import GRID_ORDER, frozen_grids, grid_differences


def test_frozen_grid_order_and_policies() -> None:
    spec = {
        "coach_feature_grids": {
            "pruning": "none",
            "radii_adjustment": "none",
            "fitting_reference": {"radial": 250, "angular": 974, "id": "250974"},
            "practical": {"radial": 99, "angular": 590, "id": "99590"},
            "coarse_analysis": {"radial": 75, "angular": 302, "id": "75302"},
        }
    }
    grids = frozen_grids(spec)
    assert tuple(grids) == GRID_ORDER
    assert grids["fitting_reference"] == {
        "id": "250974",
        "radial": 250,
        "angular": 974,
        "pruning": "none",
        "radii_adjustment": "none",
    }


def test_grid_difference_summaries() -> None:
    reference = np.zeros((3, 96))
    practical = np.ones((3, 96))
    coarse = np.full((3, 96), -2.0)
    report = grid_differences(
        {
            "fitting_reference": reference,
            "practical": practical,
            "coarse_analysis": coarse,
        }
    )
    assert report["practical"]["comparison_minus_reference_max_abs_hartree"] == 1.0
    assert report["practical"]["comparison_minus_reference_l1_hartree"] == 288.0
    assert report["coarse_analysis"]["comparison_minus_reference_max_abs_hartree"] == 2.0
    assert report["coarse_analysis"]["comparison_minus_reference_l1_hartree"] == 576.0
