"""Offline diagnostics tests, awaiting pre-test commit."""
import io
import json
from types import SimpleNamespace
import numpy as np
import pytest
from revwb97m2.scripts import k14_diagnostic_v1 as d
from revwb97m2.fit_spec import load_fit_settings


def test_feasible_start_matches_residuals_and_audit():
    rng=np.random.default_rng(0)
    arrays=dict(feature_matrix=rng.normal(size=(1498,292)),target=np.ones(1498),objective_weight=np.ones(1498))
    c,z,r,a=d.feasible_start(arrays,load_fit_settings())
    assert a['passed'] and z.sum()==4 and c[288]==1. and np.all(c[:288]==0)
    np.testing.assert_array_equal(r,arrays['feature_matrix']@c-arrays['target'])
    assert np.isclose(r@r,a['weighted_sse_hartree2'])


@pytest.mark.parametrize('value,state',[(1.,'finite'),(float('inf'),'positive_infinity'),
    (float('-inf'),'negative_infinity'),(float('nan'),'nan'),(1e100,'solver_infinity_sentinel')])
def test_nonfinite_telemetry_is_strict_json(value,state):
    result=d.numeric(value);assert result['state']==state
    json.dumps(result,allow_nan=False)
    if state!='finite':assert result['value'] is None


def test_disabled_release_does_not_run_git(tmp_path,monkeypatch):
    file=tmp_path/'release.json';d.write(file,dict(user_approved_submission=False))
    monkeypatch.setattr(d,'check_plan',lambda:{})
    monkeypatch.setattr(d.subprocess,'check_output',lambda *a,**k:pytest.fail('git reached'))
    with pytest.raises(ValueError,match='disabled'):d.check_release(file)


def test_callback_only_allows_start_messages():
    C=SimpleNamespace(MESSAGE=1,MSG_STRING=2)
    stream=io.StringIO();callback,errors=d.progress_callback(stream,SimpleNamespace(Callback=C))
    for message in ['WLSSECRET=never-log-this','Set parameter LICENSEID to value123','Loaded user MIP start with objective32']:
        callback(SimpleNamespace(cbGet=lambda key:message,terminate=lambda:pytest.fail('terminate')),1)
    assert errors==[] and 'never-log' not in stream.getvalue() and 'LICENSEID' not in stream.getvalue()
    assert json.loads(stream.getvalue())['event']=='start_message'


def test_callback_error_terminates_and_records_type():
    stream=io.StringIO();callback,errors=d.progress_callback(stream,SimpleNamespace(Callback=SimpleNamespace()))
    stopped=[];callback(SimpleNamespace(terminate=lambda:stopped.append(True)),10)
    assert errors==['AttributeError'] and stopped==[True]


def test_overwrite_refused(tmp_path,monkeypatch):
    import sys
    monkeypatch.setitem(sys.modules,'gurobipy',SimpleNamespace())
    with pytest.raises(ValueError,match='preserve'):d.solve(tmp_path,{},None,None)
