"""Prepared pre-commit regression tests; no solver or WLS needed."""
import importlib.util
import numpy as np
import pytest
from revwb97m2 import selective_grid_v1 as p
from revwb97m2.scripts import selective_recovery_v1 as v


def fixture():
    arrays = dict(feature_matrix=np.zeros((4, 292)), target=np.ones(4), objective_weight=np.ones(4),
        grid_difference_99590=np.zeros((4, 292)), grid_difference_75302=np.zeros((4, 292)))
    beta = np.zeros(292)
    beta[0] = .8
    beta[288] = .2
    beta[289:] = .1
    z = np.zeros(292)
    z[[0, 288, 289, 290, 291]] = 1
    return arrays, beta, z, p.settings(), ['a', 'b', 'c', 'd']


def test_additional_rows_exclude_candidate_union():
    d = np.array([[10., 0], [9, 0], [0, 8], [0, 7]])
    assert p.select_rows(d, [[1, 0]], 1, 2).tolist() == [0, 1, 2]


def test_multiple_candidates_deduplicated_then_add_remaining():
    d = np.array([[10., 0], [9, 0], [0, 8], [0, 7]])
    assert p.select_rows(d, [[1, 0], [0, 1], [1, 0]], 1, 1).tolist() == [0, 1, 2]


def test_matches_original_coach_including_ties():
    path = v.ROOT / 'coach/2_optimization/coachopt/select_diff_constraints.py'
    spec = importlib.util.spec_from_file_location('original_coach_selection', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    rng = np.random.default_rng(7)
    d = rng.integers(-2, 3, size=(50, 9)).astype(float)
    b = rng.integers(-1, 2, size=(3, 9)).astype(float)
    assert np.array_equal(d[p.select_rows(d, b, 5, 12)], module.select_diff_constraint_rows(d, list(b), 5, 12))


def test_small_pool_and_zero_counts():
    d = np.eye(3)
    assert p.select_rows(d, [[1, 0, 0]], 100, 200).tolist() == [0, 1, 2]
    assert p.select_rows(d, [[1, 0, 0]], 0, 0).size == 0


@pytest.mark.parametrize('d,b,n', [(np.eye(2), [], 1), (np.eye(2), [[1]], 1),
    ([[np.nan]], [[1]], 1), ([[1]], [[np.inf]], 1), ([[1]], [[1]], -1)])
def test_invalid_selector_inputs(d, b, n):
    with pytest.raises(ValueError):
        p.select_rows(d, b, n, 2)


def test_unselected_violation_reported_not_blocked():
    arrays, b, z, s, ids = fixture()
    arrays['grid_difference_99590'][1, 0] = 1
    r = p.audit(arrays, b, z, 80, np.array([0]), s, ids)
    assert r['passed'] and r['advancement_passed'] and r['review_required']
    assert not r['full_grid_passed'] and r['final_model_user_review_required']
    assert r['grids']['99590']['violations'][0]['entry'] == 'b'
    assert not r['grids']['99590']['violations'][0]['selected']


def test_selected_violation_still_blocks():
    arrays, b, z, s, ids = fixture()
    arrays['grid_difference_99590'][0, 0] = 1
    r = p.audit(arrays, b, z, 80, np.array([0]), s, ids)
    assert not r['passed'] and not r['advancement_passed']


def test_physical_failure_still_blocks():
    arrays, b, z, s, ids = fixture()
    b[0] = .7
    assert not p.audit(arrays, b, z, 80, np.array([0]), s, ids)['passed']


def test_coarse_grid_monitor_only():
    arrays, b, z, s, ids = fixture()
    arrays['grid_difference_75302'][1, 0] = 1
    r = p.audit(arrays, b, z, 80, np.array([0]), s, ids)
    assert r['passed'] and r['full_grid_passed'] and r['grids']['75302']['count'] == 1


@pytest.mark.parametrize('rows', [np.array([0, 0]), np.array([-1]), np.array([4]), np.array([.5])])
def test_invalid_rows_rejected(rows):
    arrays, b, z, s, ids = fixture()
    with pytest.raises(ValueError):
        p.audit(arrays, b, z, 80, rows, s, ids)


def test_restart_uses_same_rows_and_new_start(tmp_path):
    arrays, b, z, s, ids = fixture()
    for name in ('discovery14', 'discovery80', 'constrained80'):
        (tmp_path / name).mkdir()
        np.save(tmp_path / name / 'coefficients.npy', b)
        np.save(tmp_path / name / 'selection.npy', z)
    first = v.inputs(v.schedule()[0], tmp_path, arrays, s)
    second = v.inputs(v.schedule()[1], tmp_path, arrays, s)
    assert np.array_equal(first[2], second[2])
    assert v.schedule()[0]['start'] == 'discovery80'
    assert v.schedule()[1]['start'] == 'constrained80'


def test_disabled_release(tmp_path, monkeypatch):
    plan, release = tmp_path / 'plan.json', tmp_path / 'release.json'
    v.c.write(plan, {})
    v.c.write(release, dict(submission_authorized=False))
    monkeypatch.setattr(v, 'PLAN', plan)
    with pytest.raises(ValueError, match='disabled'):
        v.check(release)


def test_policy_change_rejected(tmp_path, monkeypatch):
    config = tmp_path / 'policy.yaml'
    config.write_text('acceptance: all_rows\n')
    monkeypatch.setattr(p, 'CONFIG', config)
    with pytest.raises(ValueError, match='unsupported'):
        p.settings()
