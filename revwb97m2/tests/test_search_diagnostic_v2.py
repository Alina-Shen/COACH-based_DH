"""The unlimited NodeLimit must not break strict JSON before optimization."""
import json
import pytest
from revwb97m2.scripts import search_diagnostic_v2 as s
from revwb97m2.scripts import search_diagnostic_v1 as old


@pytest.mark.parametrize('value',[float('inf'),-float('inf'),float('nan')])
def test_nonfinite_parameter_serializable(value):
    encoded=s.parameter_value(value)
    assert encoded['value'] is None
    json.dumps(encoded,allow_nan=False)


@pytest.mark.parametrize('value',[-1,1,2,600.,1e-12])
def test_finite_parameters_unchanged(value):
    assert s.parameter_value(value)==value


def test_scientific_scope_unchanged():
    assert s.CASES==old.CASES and s.SUPPORT==old.SUPPORT
