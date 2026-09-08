"""Offline safety and contract tests for the generic wrapper."""
from pathlib import Path
import json
import numpy as np
import pytest
from revwb97m2.scripts import generate_training_features as generation


def test_selection_ignores_partial_and_is_deterministic():
    rows = [dict(species=str(i), coverage='no_feature_candidates', requested_memory_gib='14', orbital_aos=i+1) for i in range(20)]
    rows[0]['coverage'] = 'unvalidated_or_legacy_candidates'
    rows[1]['requested_memory_gib'] = '227'
    assert generation.choose_first(rows) == generation.choose_first(list(reversed(rows)))
    assert len(generation.choose_first(rows)) == 16
    assert generation.choose_first(rows)[0]['species'] == '2'
    with pytest.raises(ValueError):
        generation.choose_first(rows, 100)


@pytest.mark.parametrize('name', ['', '.', '..', '../escape', '/absolute'])
def test_unsafe_name(name):
    with pytest.raises(ValueError):
        generation.safe_name(name)


def test_missing_release_fails_before_mutation(tmp_path, monkeypatch):
    monkeypatch.setattr(generation, 'load', lambda p: ({}, None))
    with pytest.raises(ValueError, match='release absent'):
        generation.run(tmp_path/'plan', 'H', None, 8, 14)
    assert list(tmp_path.iterdir()) == []


def test_release_requires_all_seven(tmp_path):
    plan = tmp_path/'plan'
    plan.write_text('{}')
    release = tmp_path/'release'
    release.write_text(json.dumps(dict(plan_sha256=generation.native.digest(plan),
        user_approved_submission=True, resource_review_passed=True, canaries={})))
    with pytest.raises(ValueError, match='all seven'):
        generation.release_check(plan, release)


def test_reuse_stale_plan_rejected(tmp_path):
    plan = tmp_path/'plan'
    plan.write_text('{}')
    with pytest.raises(ValueError, match='reuse plan changed'):
        generation.validate_reuse(dict(plan=str(plan), plan_sha256='wrong'), 'H')


def test_d4_tolerance_only():
    a = np.arange(292, dtype=float)
    b = a.copy()
    b[-1] += 1e-13
    generation.compare_vectors(a, b)
    b[0] += 1e-14
    with pytest.raises(ValueError, match='non-D4'):
        generation.compare_vectors(a, b)


def test_completed_stage_reuses_without_run(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(generation.native, 'validate_stage', lambda *a: calls.append('validated'))
    monkeypatch.setattr(generation.native, 'run_native', lambda *a: pytest.fail('native run forbidden'))
    generation.native.run_stage(tmp_path, 'scalar', 'input', {}, 'hash', 8)
    assert calls == ['validated']


def test_partial_stage_fails_without_run(tmp_path, monkeypatch):
    monkeypatch.setattr(generation.native, 'run_native', lambda *a: pytest.fail('native run forbidden'))
    with pytest.raises(FileNotFoundError):
        generation.native.run_stage(tmp_path, 'scalar', 'input', {}, 'hash', 8)


def test_completed_refresh_reuse_normalizes_fixed_energy(tmp_path, monkeypatch):
    from revwb97m2 import v7_refresh
    p = tmp_path/'plan'
    p.write_text('{}')
    monkeypatch.setattr(v7_refresh, 'validate_species', lambda *a: (np.zeros(292), -1.5, {}))
    _, fixed, _ = generation.validate_reuse(dict(kind='refresh', plan=str(p),
                                      plan_sha256=generation.native.digest(p)), 'H')
    assert fixed == {'fixed_energy_hartree': -1.5}
