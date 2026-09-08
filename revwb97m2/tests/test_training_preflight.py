"""Planning-only regression checks; no chemistry or scheduler operations."""
import json
import pytest
from revwb97m2.scripts.prepare_training_preflight import (
    digest, publication, select_pilot, stoichiometry, unique,
)


@pytest.mark.parametrize('value', ['1,A,2', 'nan,A', '0,A', '1,'])
def test_invalid_stoichiometry(value):
    with pytest.raises(ValueError):
        stoichiometry(value)


def test_signed_stoichiometry_and_duplicates():
    assert stoichiometry('1,A,-2,B')[1] == {'coefficient': -2., 'species': 'B'}
    with pytest.raises(ValueError):
        unique([{'id': 'a'}, {'id': 'a'}], 'id')


def test_selection_is_nested_deterministic_and_covers_groups():
    entries = [dict(reaction=str(i), global_index=i, si_row_index=str(i % 3),
                    property_class=str(i % 2), species=[str(i)], objective_weight=i+1)
               for i in range(12)]
    inventory = {str(i): dict(requested_memory_gib=14, orbital_aos=i+1) for i in range(12)}
    first = select_pilot(entries, ['10', '11'], inventory, set(), 6)
    assert first == select_pilot(list(reversed(entries)), ['10', '11'], inventory, set(), 6)
    assert {'10', '11'} <= {r['reaction'] for r in first}
    assert len(first) == 6
    assert len({r['si_row_index'] for r in first}) == 3
    assert all(r['objective_weight'] == int(r['reaction'])+1 for r in first)


def test_publication_requires_hashes_and_completion(tmp_path):
    (tmp_path/'data').write_text('original')
    (tmp_path/'species.json').write_text(json.dumps(dict(plan_sha256='p',
        specification_sha256='s', artifacts={'data': digest(tmp_path/'data')})))
    assert publication(tmp_path, 'p', 's', 'DONE')['status'] == 'publication_without_accepted_completion'
    (tmp_path/'DONE').touch()
    assert publication(tmp_path, 'p', 's', 'DONE')['status'] == 'completion_evidence_hash_verified'
    (tmp_path/'data').write_text('corrupt')
    assert publication(tmp_path, 'p', 's', 'DONE')['status'] == 'evidence_failure'


def test_stale_spec_rejected(tmp_path):
    (tmp_path/'species.json').write_text(json.dumps(dict(plan_sha256='p', specification_sha256='old')))
    assert publication(tmp_path, 'p', 'new', 'DONE')['status'] == 'evidence_failure'
