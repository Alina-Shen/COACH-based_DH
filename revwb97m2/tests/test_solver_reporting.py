import json
import math
import pytest
from revwb97m2.solver_reporting import gap_report,raw_gap_from_record,strict_dumps


@pytest.mark.parametrize('raw,state',[(math.inf,'positive_infinity'),(-math.inf,'negative_infinity'),(math.nan,'nan')])
def test_nonfinite_gap_is_explicit_and_strict(raw,state):
    r=gap_report(3.5e-7,1e-16,raw)
    assert r['gap'] is None and r['gap_state']==state
    assert r['gap_recomputed']==pytest.approx(1.)
    assert json.loads(strict_dumps(r))==r
    restored=raw_gap_from_record(r)
    assert math.isnan(restored) if math.isnan(raw) else restored==raw


@pytest.mark.parametrize('obj,bound,raw,expected',[(2.,1.,.5,.5),(-2.,-3.,.5,.5),(0.,0.,0.,0.),(0.,1.,math.inf,None)])
def test_gap_formula(obj,bound,raw,expected):
    r=gap_report(obj,bound,raw)
    assert r['gap_recomputed']==expected and r['gap_consistent']


def test_legacy_and_mismatch():
    assert raw_gap_from_record({'gap':math.inf})==math.inf
    assert gap_report(3.5e-7,0.,math.inf)['gap_consistent'] is False
    with pytest.raises(ValueError):
        strict_dumps({'unexpected':math.inf})
