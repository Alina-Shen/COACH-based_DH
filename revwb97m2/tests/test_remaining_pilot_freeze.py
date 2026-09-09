import pytest
from revwb97m2.scripts.freeze_remaining_pilot_v3 import select_groups


def row(name, category='new_generation_requires_frozen_execution_manifest', error=None, memory=14):
    return dict(species=name, category=category, input_gate_error=error,
                resources=dict(cpus=8, requested_memory_gib=memory, wall_hours=72))


def test_scope_excludes_completed_legacy_and_blocked():
    rows = [row('new'), row('legacy', 'legacy_candidate_requires_stage_migration'),
            row('first16', 'first16_frozen_not_launched'), row('ecp', error='ECP unsupported'),
            row('canary', 'corrected_canary_validated')]
    assert select_groups(rows) == {(8,14,72): ['new']}


def test_groups_preserve_resources_and_sort():
    assert select_groups([row('z'),row('a'),row('b',memory=21)]) == {
        (8,14,72): ['a','z'], (8,21,72): ['b']}


def test_duplicate_species_rejected():
    with pytest.raises(ValueError, match='duplicate'):
        select_groups([row('a'),row('a')])


def test_unreviewed_memory_rejected():
    with pytest.raises(ValueError, match='unreviewed resource'):
        select_groups([row('a',memory=15)])
