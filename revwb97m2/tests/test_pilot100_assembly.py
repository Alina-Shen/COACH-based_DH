import numpy as np
import pytest
from revwb97m2.scripts.assemble_pilot100_v1 import assemble_checked


def fixture():
    records={f's{i}':(np.full(292,i/100),{'fixed_energy_hartree':i/10},
        {g:np.full(292,i/10000) for g in ('99590','75302')}) for i in range(224)}
    reactions=[dict(reaction=f'r{i}',reference_hartree=float(i),objective_weight=0.5+i,
        stoichiometry=[dict(species=f's{j}',coefficient=(-1.)**j) for j in range(i,224,100)]) for i in range(100)]
    return reactions,records


def test_exact_matrix_and_original_weights():
    reactions,records=fixture();arrays,names=assemble_checked(reactions,records)
    assert len(names)==224 and arrays['feature_matrix'].shape==(100,292)
    np.testing.assert_array_equal(arrays['objective_weight'],np.arange(100)+0.5)


def test_missing_species_refused():
    reactions,records=fixture();del records['s223']
    with pytest.raises(Exception,match='exact224'):assemble_checked(reactions,records)


def test_partial_pilot_refused():
    reactions,records=fixture()
    with pytest.raises(Exception,match='exact100'):assemble_checked(reactions[:-1],records)


def test_nonfinite_species_refused():
    reactions,records=fixture();records['s0'][0][0]=np.nan
    with pytest.raises(ValueError,match='invalid 292'):assemble_checked(reactions,records)
