import numpy as np
import pytest
from revwb97m2 import selected_full_v1 as f
from revwb97m2 import selected_submit_v1 as s


def test_138_pool_and_414_selected_tasks():
    g = f.task_graph()
    assert len(g['tasks']) == len({t['id'] for t in g['tasks']}) == 552
    assert len(g['grid_selection']['candidate_pool']) == 138
    selected = [t for t in g['tasks'] if t['phase'] == 2]
    assert len(selected) == 414
    assert {t['budget'] for t in selected} == set(range(14, 83))
    assert all(t['dependencies'] == ['grid_selection'] for t in selected)


def test_all_sources_matching_k_and_no_dedup():
    g = f.task_graph()
    for k in range(14, 83):
        tasks = [t for t in g['tasks'] if t['phase'] == 2 and t['budget'] == k]
        assert [t['start_source'] for t in tasks] == ['simple', 'simple',
            f'p1_k{k}_simple_r0', f'p1_k{k}_simple_r0', f'p1_k{k}_simple_r1', f'p1_k{k}_simple_r1']


def test_discovery_noise_is_unchanged_and_pass2_reproducible():
    g = f.task_graph()
    expected = [t for t in f.old.planner.task_graph()['tasks'] if t['phase'] == 1] + f.e.additional_tasks()
    assert [t for t in g['tasks'] if t['phase'] == 1] == expected
    assert g == f.task_graph()
    selected = [t for t in g['tasks'] if t['phase'] == 2]
    rng = np.random.default_rng(0)
    for first, second in zip(selected[::2], selected[1::2]):
        assert first['noise'] == [0.] * 292
        assert np.array_equal(second['noise'], rng.normal(scale=.05, size=292))
        assert first['start_source'] == second['start_source']


def test_submission_barriers_and_session_limit(tmp_path):
    route = dict(partition='cm1', account='lr_qchem', qos='condo_qchem')
    grid = s.command(route, tmp_path / 'release', 'grid')
    selected = s.command(route, tmp_path / 'release', 'run', '123')
    assert '--dependency=afterok:25796986:25801134' in grid
    assert not any(v.startswith('--array') for v in grid)
    assert '--array=0-413%2' in selected
    assert '--dependency=afterok:123' in selected
    with pytest.raises(ValueError, match='dependency'):
        s.command(route, tmp_path / 'release', 'run')


def test_release_disabled(monkeypatch, tmp_path):
    path = tmp_path / 'p.json'
    f.old.c.write(path, {})
    monkeypatch.setattr(f, 'PLAN', path)
    with pytest.raises(ValueError, match='disabled'):
        f.check(path)


def test_failed_source_audit_prevents_snapshot(monkeypatch, tmp_path):
    root = tmp_path / 'snapshot'
    monkeypatch.setattr(f, 'check', lambda _: ({}, {'route': {}}, {}, root))
    monkeypatch.setattr(f.old.c.d.full, 'check_allocation', lambda _: None)
    def reject(_):
        raise ValueError('source incomplete')
    monkeypatch.setattr(f.e, 'validate', reject)
    with pytest.raises(ValueError, match='source incomplete'):
        f.prepare_grid(tmp_path / 'release')
    assert not root.exists()
