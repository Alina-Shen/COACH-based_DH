"""Regression for observed cross-node ridge rounding and strict audit structure."""
import copy
import numpy as np
import pytest
from revwb97m2 import selective_readback_v2 as r
from revwb97m2.tests.test_selective_recovery_v1 import fixture


def test_observed_last_bit_difference_passes():
    r.compare_report({'ridge': 2.7935240616529565e-6}, {'ridge': 2.793524061652957e-6})


@pytest.mark.parametrize('actual,saved', [
    (1.0, 1.000001), (0.0, 1e-12), (float('nan'), float('nan')),
    (float('inf'), float('inf')), (True, 1), (1, 1.0), (False, True),
    ({'x': 1}, {'y': 1}), ([1], [1, 2]), ('id1', 'id2'), (2, 3)])
def test_meaningful_or_structural_changes_rejected(actual, saved):
    with pytest.raises(ValueError):
        r.compare_report(actual, saved)


def test_nested_rounding_passes_but_decision_change_does_not():
    report = {'passed': True, 'rows': [1, 2], 'data': [{'value': 2.7935240616529565e-6}]}
    saved = copy.deepcopy(report)
    saved['data'][0]['value'] = 2.793524061652957e-6
    r.compare_report(report, saved)
    saved['passed'] = False
    with pytest.raises(ValueError):
        r.compare_report(report, saved)


def test_reader_recomputes_selected_feasibility_before_comparison(tmp_path, monkeypatch):
    arrays, b, z, settings, ids = fixture()
    folder = tmp_path / 'constrained80'
    folder.mkdir()
    rows = np.array([0])
    start = b.copy()
    for name, value in [('start_coefficients', start), ('start_selection', z),
                        ('grid_rows', rows), ('coefficients', b), ('selection', z)]:
        np.save(folder / (name + '.npy'), value)
    monkeypatch.setattr(r.v, 'inputs', lambda *args: (start, z, rows))
    params = dict(settings.solver_parameters)
    params.update(Threads=16, TimeLimit=600, Seed=settings.seed)
    r.v.c.write(folder / 'model.json', dict(variables=584, constraints=592, binaries=292, sos=0, parameters=params))
    r.v.c.write(folder / 'result.json', dict(name='constrained80', budget=80, passed=True,
        status=9, solution_count=1, callback_errors=[]))
    arrays['grid_difference_99590'][0, 0] = 1
    # Store a consistent (infeasible-for-grid but valid ungridded) start report.
    r.v.c.write(folder / 'start_audit.json', r.v.a.start_audit(arrays, start, z, 80, rows, settings))
    with pytest.raises(ValueError, match='candidate infeasible'):
        r.audit_case(dict(name='constrained80'), tmp_path, arrays, settings, ids)
