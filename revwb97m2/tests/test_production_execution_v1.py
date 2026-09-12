from types import SimpleNamespace
import numpy as np
import pytest
from revwb97m2 import production_multistart_v1 as r
from revwb97m2 import production_submit_v1 as s


def test_noisy_infeasible_start_remains_a_suggestion(monkeypatch, tmp_path):
    task = r.planner.task_graph()['tasks'][1]
    seed = np.zeros(292)
    monkeypatch.setattr(r.v.policy, 'audit', lambda *args: {'passed': False})
    original, beta, z, diagnostic = r.start_inputs(task, tmp_path, {'simple_seed': seed},
                                                   {}, [], None, np.array([], dtype=int))
    assert not diagnostic['passed']
    assert np.array_equal(beta, seed + task['noise'])
    assert np.count_nonzero(z) == 292
    assert np.array_equal(original, seed)


def test_mandatory_zero_scalar_still_selected():
    z = r.selection_guess(np.zeros(292))
    assert np.array_equal(np.flatnonzero(z), [288, 289, 290, 291])


def test_build_overrides_bounded_search_time(monkeypatch):
    model = SimpleNamespace(Params=SimpleNamespace(TimeLimit=600, Threads=16))
    monkeypatch.setattr(r.v.a, 'build', lambda *args: (model, [], []))
    result = r.build({}, None, {'budget': 14, 'seconds': 7200, 'threads': 16}, [], None)
    assert result[0].Params.TimeLimit == 7200


def test_publication_detects_changed_and_extra_files(tmp_path):
    r.c.write(tmp_path / 'a.json', {'x': 1})
    r.publish(tmp_path)
    r.verify_publication(tmp_path)
    r.c.write(tmp_path / 'extra.json', {})
    with pytest.raises(ValueError, match='unexpected artifacts'):
        r.verify_publication(tmp_path)


def test_failure_marker_blocks_readback(tmp_path):
    folder = tmp_path / 'task'
    folder.mkdir()
    r.c.write(folder / 'failure.json', {})
    with pytest.raises(ValueError, match='failure marker'):
        r.audit_task({'id': 'task'}, tmp_path, {}, {}, [], None, [])


def test_draft_cannot_release(monkeypatch, tmp_path):
    path = tmp_path / 'plan.json'
    r.c.write(path, {})
    monkeypatch.setattr(r, 'PLAN', path)
    with pytest.raises(ValueError, match='release disabled'):
        r.check(path)


def test_array_dependencies_and_no_requeue(tmp_path):
    route = dict(partition='cm1', account='lr_qchem', qos='condo_qchem')
    one = s.command(route, tmp_path / 'release', '1')
    grid = s.command(route, tmp_path / 'release', 'grid', '123')
    two = s.command(route, tmp_path / 'release', '2', '124')
    assert '--array=0-13' in one and '--array=0-41' in two
    assert not any(x.startswith('--array') for x in grid)
    assert '--dependency=afterok:123' in grid and '--dependency=afterok:124' in two
    assert all('--no-requeue' in cmd for cmd in [one, grid, two])
    assert '--kill-on-invalid-dep=yes' in two


@pytest.mark.parametrize('active,additional', [(985, 14), (957, 42), (998, 1)])
def test_queue_cap_rejects_overflow(active, additional):
    with pytest.raises(ValueError, match='998'):
        s.check_capacity(active, additional)


def test_queue_cap_accepts_exact_limit():
    s.check_capacity(956, 42)


def test_low_priority_route_rejected(tmp_path):
    with pytest.raises(ValueError, match='route'):
        s.command(dict(partition='lr_lowprio', account='mhg', qos='normal'), tmp_path / 'r', '1')


def test_wrong_k_parent_rejected(tmp_path):
    task = dict(start_source='parent', budget=14)
    with pytest.raises(ValueError, match='wrong-K'):
        r.start_inputs(task, tmp_path, {'tasks': [dict(id='parent', phase=1, budget=80)]},
                       {}, [], None, [])


def test_grid_publication_uses_all_fourteen_candidates(monkeypatch, tmp_path):
    graph = r.planner.task_graph()
    calls = []
    monkeypatch.setattr(r, 'audit_task', lambda task, *args: calls.append(task['id']))
    for i, name in enumerate(graph['grid_selection']['candidate_pool']):
        folder = tmp_path / name
        folder.mkdir()
        np.save(folder / 'coefficients.npy', np.full(292, i))
        r.c.write(folder / 'publication.json', {})
    def select(d, candidates, per, extra):
        assert candidates.shape == (14, 292)
        assert (per, extra) == (100, 200)
        return np.array([0, 1], dtype=int)
    monkeypatch.setattr(r.v.policy, 'select_rows', select)
    arrays = {'grid_difference_99590': np.zeros((2, 292))}
    r.select_grid(tmp_path, graph, arrays, [], None, write=True)
    assert calls == graph['grid_selection']['candidate_pool']
    assert np.array_equal(r.select_grid(tmp_path, graph, arrays, [], None), [0, 1])


def test_one_failed_discovery_blocks_grid_publication(monkeypatch, tmp_path):
    def reject(*args):
        raise ValueError('discovery invalid')
    monkeypatch.setattr(r, 'audit_task', reject)
    with pytest.raises(ValueError, match='discovery invalid'):
        r.select_grid(tmp_path, r.planner.task_graph(), {}, [], None, write=True)
    assert not (tmp_path / 'grid_selection').exists()
