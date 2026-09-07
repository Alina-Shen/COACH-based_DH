"""New canary tests: added before the user's pre-test commit; not yet run."""
from pathlib import Path
import pytest
from revwb97m2 import v7_canary as c
from revwb97m2.fit_spec import load_fit_settings
from revwb97m2.qchem_scalar_features import derive_scalar_input


def source(atom='H', multiplicity=2):
    return (f'$molecule\n0 {multiplicity}\n{atom} 0 0 0\n$end\n'
            '$rem\nMETHOD wB97M-V\nSCF_GUESS READ\nUNRESTRICTED TRUE\n'
            'AUX_BASIS_CORR rimp2-aug-cc-pVTZ\n$end\n')


def test_one_electron_detection_is_not_name_based():
    assert c.electron_count(source()) == (1, 1)
    assert 'pt2' not in c.stage_inputs(source(), load_fit_settings())
    assert 'pt2' in c.stage_inputs(source('He', 1), load_fit_settings())


@pytest.mark.parametrize('text', [source('@H'), source('H', 1),
                                 source()+'$ecp\nH\n$end\n'])
def test_unsupported_electron_inputs_fail_closed(text):
    with pytest.raises(ValueError):
        c.electron_count(text)


def test_v7_inputs_and_legacy_default_remain_distinct():
    inputs = c.stage_inputs(source(), load_fit_settings())
    assert set(inputs) == {'250974', '99590', '75302', 'scalar', 'fixed'}
    assert 'NL_VV_B 550' in inputs['scalar']
    assert 'NL_VV_B 1000' in derive_scalar_input(source())[0]
    for text in inputs.values():
        assert 'MAX_SCF_CYCLES 0' in text
        assert 'SCF_GUESS READ' in text
        assert 'MP2_RESTART_NO_SCF TRUE' in text


def test_output_counts_and_read_evidence():
    text = ('Reading MOs from coefficient file\n'*2 +
            'There are 1 alpha and 0 beta electrons\n'
            'Thank you very much for using Q-Chem')
    c.output_checks(text, 1, 1)
    with pytest.raises(ValueError):
        c.output_checks(text, 2, 0)
    with pytest.raises(ValueError):
        c.output_checks(text.replace('Thank you', 'Other'), 1, 1)


def test_partial_stage_is_not_overwritten(tmp_path):
    stage = tmp_path/'partial'
    stage.mkdir()
    (stage/'keep').write_text('evidence')
    with pytest.raises(FileNotFoundError):
        c.run_stage(stage, 'scalar', 'input', {}, 'hash', 8)
    assert (stage/'keep').read_text() == 'evidence'


def test_exclusive_manifest_write(tmp_path):
    p = tmp_path/'plan.json'
    c.write(p, {'value': 1})
    with pytest.raises(FileExistsError):
        c.write(p, {'value': 2})
    assert c.read(p) == {'value': 1}


def test_stage_readback_rejects_tampering(tmp_path):
    scratch = tmp_path/'qcscratch/canary'
    scratch.mkdir(parents=True)
    (scratch/'qarchive.h5').write_bytes(b'archive')
    (tmp_path/'input.q3.in').write_text('input')
    (tmp_path/'qchem.out').write_text(
        'Reading MOs from coefficient file\n'*2 +
        'There are 1 alpha and 0 beta electrons\nThank you very much for using Q-Chem')
    case = dict(species='TMD01_H', electron_count=1, spin=1,
                qarchive_sha256=c.digest(scratch/'qarchive.h5'))
    c.write(tmp_path/'STAGE_COMPLETE.json', dict(plan_sha256='plan', species='TMD01_H',
            artifacts={n: c.digest(tmp_path/n) for n in ('input.q3.in', 'qchem.out')}))
    c.validate_stage(tmp_path, 'input', case, 'plan')
    (tmp_path/'qchem.out').write_text('changed')
    with pytest.raises(ValueError, match='stage artifacts'):
        c.validate_stage(tmp_path, 'input', case, 'plan')


def test_large_review_gate_precedes_execution(monkeypatch):
    case = {'species': c.NAMES[-1]}
    monkeypatch.setattr(c, 'load_plan', lambda p: ({'cases': [case]}, None))
    with pytest.raises(ValueError, match='review'):
        c.run(Path('unused'), case['species'], 16, 557)
