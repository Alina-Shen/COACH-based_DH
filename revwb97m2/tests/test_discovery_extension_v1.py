import numpy as np
import pytest
from revwb97m2 import discovery_extension_v1 as e


def test_complete_138_pool_without_duplicate_tasks():
    original = [t for t in e.old.planner.task_graph()['tasks'] if t['phase'] == 1]
    added = e.additional_tasks()
    assert len(added) == 124
    full = original + added
    assert len(full) == len({t['id'] for t in full}) == 138
    assert sorted({t['budget'] for t in full}) == list(range(14, 83))
    assert all(sum(t['budget'] == k for t in full) == 2 for k in range(14, 83))


def test_noise_continues_existing_sweep():
    rng = np.random.default_rng(0)
    for _ in range(7):
        rng.normal(scale=.05, size=292)
    tasks = e.additional_tasks()
    assert tasks[0]['budget'] == 15
    assert np.array_equal(tasks[0]['noise'], np.zeros(292))
    assert np.array_equal(tasks[1]['noise'], rng.normal(scale=.05, size=292))
    assert tasks == e.additional_tasks()
    assert all(t['seconds'] == 7200 and t['threads'] == 16 and t['phase'] == 1 for t in tasks)


def test_no_license_overlap_in_launcher():
    text = (e.old.ROOT / 'revwb97m2/slurm/run_discovery_extension_v1.sh').read_text()
    assert '#SBATCH --array=0-123%2' in text
    assert '#SBATCH --dependency=afterok:25796986' in text
    assert '#SBATCH --no-requeue' in text


def test_disabled_extension_release(monkeypatch, tmp_path):
    path = tmp_path / 'plan.json'
    e.old.c.write(path, {})
    monkeypatch.setattr(e, 'PLAN', path)
    with pytest.raises(ValueError, match='release disabled'):
        e.check(path)
