"""New refresh tests; execute only after the requested pre-chemical commit."""
import numpy as np
import pytest
from revwb97m2.v7_refresh import checked_vector, independently_check_assembly,write
from revwb97m2.reaction_assembly import assemble_reaction_arrays


def test_publication_never_overwrites(tmp_path):
    path=tmp_path/'record.json';write(path,{'first':True})
    with pytest.raises(FileExistsError):write(path,{'second':True})


def test_vector_rejects_nonfinite_and_wrong_shape(tmp_path):
    path=tmp_path/'vector.npy'
    for array in (np.zeros(291),np.full(292,np.nan)):
        np.save(path,array)
        with pytest.raises(ValueError):checked_vector(path)


def test_independent_reaction_assembly_detects_tampering():
    names=['A','B'];vectors={'A':np.arange(292,dtype=float),'B':np.ones(292)}
    fixed={'A':-5.,'B':-2.}
    differences={n:{g:np.zeros(292) for g in ('99590','75302')} for n in names}
    reactions=[{'reaction':'A_minus_2B','reference_hartree':-.9,'objective_weight':2.,
                'stoichiometry':[{'species':'A','coefficient':1},{'species':'B','coefficient':-2}]}]
    result=assemble_reaction_arrays(reactions,vectors,fixed,differences,('99590','75302'))
    independently_check_assembly(reactions,names,vectors,fixed,differences,result)
    result['feature_matrix'][0,289]+=1e-5
    with pytest.raises(ValueError):
        independently_check_assembly(reactions,names,vectors,fixed,differences,result)


def test_vv10_only_change_does_not_change_target():
    names=['A'];vector=np.ones(292);fixed={'A':-2.}
    diffs={'A':{g:np.zeros(292) for g in ('99590','75302')}}
    rows=[{'reaction':'A','reference_hartree':-1.,'objective_weight':3.,
           'stoichiometry':[{'species':'A','coefficient':1}]}]
    before=assemble_reaction_arrays(rows,{'A':vector},fixed,diffs,('99590','75302'))
    vector=vector.copy();vector[289]=2.
    after=assemble_reaction_arrays(rows,{'A':vector},fixed,diffs,('99590','75302'))
    assert np.array_equal(before['target'],after['target'])
    assert np.array_equal(before['objective_weight'],after['objective_weight'])
    assert np.flatnonzero(before['feature_matrix'][0]!=after['feature_matrix'][0]).tolist()==[289]


def test_legacy_fixed_parser_preserves_validated_route(monkeypatch):
    from revwb97m2 import v7_refresh as refresh
    calls=[]
    def ordinary(text,sr):
        calls.append(('ordinary',text,sr));return {'fixed_energy_hartree':-204.75477468260002}
    def recovery(text,sr):
        calls.append(('recovery',text,sr));return {'fixed_energy_hartree':-204.7547746795}
    monkeypatch.setattr(refresh,'parse_qchem_fixed_energy_output',ordinary)
    monkeypatch.setattr(refresh,'fixed_energy',recovery)
    assert refresh.legacy_fixed_values('output',-25.,recovered=False)['fixed_energy_hartree']==-204.75477468260002
    assert refresh.legacy_fixed_values('output',-25.,recovered=True)['fixed_energy_hartree']==-204.7547746795
    assert [c[0] for c in calls]==['ordinary','recovery']
