import json
import numpy as np
import pytest
from revwb97m2.scripts import corrected_canary_evidence as evidence
from revwb97m2.scripts import generate_training_features_v2 as generation


def test_missing_release_has_no_side_effects(tmp_path, monkeypatch):
    monkeypatch.setattr(generation, 'load', lambda p: ({}, None))
    with pytest.raises(ValueError, match='release absent'):
        generation.run(tmp_path/'plan', 'H', None, 8, 14)
    assert not list(tmp_path.iterdir())


def test_legacy_evidence_not_silently_migrated():
    with pytest.raises(ValueError, match='legacy reuse'):
        generation.validate_reuse({'kind':'canary'}, 'H')


def test_exact_seven_required(tmp_path):
    p=tmp_path/'registry'
    p.write_text(json.dumps({'schema_version':1,'species':{}}))
    with pytest.raises(ValueError, match='exact seven'):
        evidence.validate_registry(p)


def test_wrong_record_marker_and_artifact_rejected(tmp_path):
    p=tmp_path/'record.json'
    (tmp_path/'array').write_text('data')
    p.write_text(json.dumps({'artifacts':{'array':evidence.v.digest(tmp_path/'array')}}))
    h=evidence.v.digest(p)
    (tmp_path/'DONE').write_text(h)
    evidence.checked_record(p,h,'DONE')
    (tmp_path/'array').write_text('changed')
    with pytest.raises(ValueError,match='artifacts changed'):
        evidence.checked_record(p,h,'DONE')
    with pytest.raises(ValueError,match='record hash'):
        evidence.checked_record(p,'wrong','DONE')
    (tmp_path/'DONE').write_text('wrong')
    with pytest.raises(ValueError,match='marker changed'):
        evidence.checked_record(p,h,'DONE')


def test_assembly_uses_corrected_fixed_and_stoichiometry():
    d={g:np.zeros(292) for g in evidence.v.GRIDS[1:]}
    records={'A':(np.ones(292),{'fixed_energy_hartree':2.},d),
             'B':(np.full(292,4.),{'fixed_energy_hartree':5.},d)}
    reaction={'reaction':'difference','stoichiometry':[{'species':'B','coefficient':1},
              {'species':'A','coefficient':-1}], 'reference_hartree':7.,'objective_weight':50.}
    result=evidence.assemble_with_evidence([reaction],records)
    assert np.array_equal(result['feature_matrix'],np.full((1,292),3.))
    assert result['target'][0]==4.
    assert result['objective_weight'][0]==50.
    with pytest.raises(KeyError):
        evidence.assemble_with_evidence([reaction],{'A':records['A']})


def test_wrong_release_registry_rejected(tmp_path):
    plan=tmp_path/'plan';plan.write_text('{}')
    r=tmp_path/'release';r.write_text(json.dumps(dict(plan_sha256=evidence.v.digest(plan),
      user_approved_submission=True,resource_review_passed=True,corrected_evidence_sha256='wrong')))
    with pytest.raises(ValueError,match='wrong release evidence'):
        generation.release_check(plan,r)
