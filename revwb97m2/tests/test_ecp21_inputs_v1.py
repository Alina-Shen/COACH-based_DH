from pathlib import Path
import pytest
from revwb97m2.scripts import ecp21_inputs_v1 as e


@pytest.mark.parametrize('index',range(21))
def test_reviewed_atomic_inputs_preserved(index):
    case=e.v.read(e.REVIEW)['cases'][index];source=Path(case['authoritative_input']).read_text();bridge=case['bridge']
    assert e.electron_count(source,bridge)==(int(bridge['electron_count']),int(bridge['spin']))
    stages=e.stage_inputs(source,e.v.load_fit_settings(),bridge)
    assert len(stages)==6
    for value in stages.values():
        for key in ('basis','ecp','molecule'):assert e.block(value,key)==e.block(source,key)
        assert 'MP2_RESTART_NO_SCF TRUE' in value


def test_source_change_refused():
    case=e.v.read(e.REVIEW)['cases'][0]
    with pytest.raises(ValueError,match='unreviewed'):
        e.electron_count(Path(case['authoritative_input']).read_text()+'\n',case['bridge'])


def test_wrong_core_refused():
    case=e.v.read(e.REVIEW)['cases'][0]
    with pytest.raises(ValueError):
        e.electron_count(Path(case['authoritative_input']).read_text(),{**case['bridge'],'ecp_electrons':'10'})


def test_wrong_spin_refused():
    case=e.v.read(e.REVIEW)['cases'][0]
    with pytest.raises(ValueError):
        e.electron_count(Path(case['authoritative_input']).read_text(),{**case['bridge'],'spin':'7'})
