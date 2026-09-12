import numpy as np
from revwb97m2 import production_multistart_plan_v1 as p


def test_56_tasks_and_full_pool_barrier():
    graph = p.task_graph()
    tasks = graph['tasks']
    assert len(tasks) == len({t['id'] for t in tasks}) == 56
    assert sum(t['phase'] == 1 for t in tasks) == 14
    assert sum(t['phase'] == 2 for t in tasks) == 42
    assert len(graph['grid_selection']['candidate_pool']) == 14
    assert all(t['dependencies'] == ['grid_selection'] for t in tasks if t['phase'] == 2)
    assert not graph['submission_authorized'] and not graph['production_executor_implemented']


def test_original_start_not_preceding_result():
    tasks = p.task_graph()['tasks']
    for i in range(0, len(tasks), 2):
        first, second = tasks[i:i+2]
        assert first['start_source'] == second['start_source']
        assert np.count_nonzero(first['noise']) == 0
        assert np.count_nonzero(second['noise']) == 292
        assert first['id'] not in second['dependencies']


def test_noise_is_reproducible_and_reset_per_pass():
    one, two = p.task_graph(), p.task_graph()
    assert one == two
    assert one['tasks'][1]['noise'] == one['tasks'][15]['noise']
    expected = np.random.default_rng(0).normal(scale=.05, size=292)
    assert np.array_equal(one['tasks'][1]['noise'], expected)


def test_simple_seed_copies_only_approved_scalar_slots():
    source = np.arange(292, dtype=float)
    seed = p.simple_seed(source)
    assert np.array_equal(seed[289:], source[289:])
    assert seed[0] == .85 and seed[288] == .15
    assert np.count_nonzero(seed[:288]) == 4


def test_noisy_start_is_not_clipped():
    original = np.zeros(292)
    original[289] = .99999999
    task = p.task_graph()['tasks'][1]
    result = p.materialize_start(task, original)
    assert np.array_equal(result, original + np.array(task['noise']))
    assert np.count_nonzero(result[:288]) == 288


def test_matching_k_source_and_no_deduplication():
    for k in p.BUDGETS:
        tasks = [t for t in p.task_graph()['tasks'] if t['phase'] == 2 and t['budget'] == k]
        assert [t['start_source'] for t in tasks] == ['simple', 'simple',
            f'p1_k{k}_simple_r0', f'p1_k{k}_simple_r0', f'p1_k{k}_simple_r1', f'p1_k{k}_simple_r1']
