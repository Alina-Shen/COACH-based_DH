import numpy as np
import pytest
from revwb97m2.grid_selection import select_rows


def test_small_cohort_selects_all():
    assert np.array_equal(select_rows(np.eye(20),np.ones((2,20))),np.arange(20))


def test_union_and_dedup():
    d=np.array([[3.,0.],[0.,4.],[2.,2.],[0.,1.]])
    assert select_rows(d,np.eye(2),1,1).tolist()==[0,1]


def test_ties_are_stable_and_bad_inputs_rejected():
    assert select_rows(np.ones((5,2)),np.ones((1,2)),1,1).tolist()==[0]
    with pytest.raises(ValueError):
        select_rows(np.ones((2,3)),np.ones((1,2)))
    with pytest.raises(ValueError):
        select_rows(np.array([[np.nan]]),np.ones((1,1)))
