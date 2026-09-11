import numpy as np
import pytest
from revwb97m2.scripts import assemble_full1498_v1 as a


def fixture():
    records = {n: (np.arange(292, dtype=float)*v, {'fixed_energy_hartree': v},
                   {g: np.r_[np.ones(288)*v/100, np.zeros(4)] for g in a.GRIDS})
               for n, v in (('a', 1.), ('b', 2.), ('c', 3.))}
    reactions = [dict(reaction='r1', set_or_subset='g1', reference_hartree=4., objective_weight=10.,
                      stoichiometry=[dict(species='a', coefficient=-1.), dict(species='b', coefficient=2.)]),
                 dict(reaction='r2', set_or_subset='g2', reference_hartree=5., objective_weight=.5,
                      stoichiometry=[dict(species='a', coefficient=-1.), dict(species='c', coefficient=1.)])]
    return reactions, records


def assemble(reactions, records):
    return a.assemble_checked(reactions, records, entries=2, species=3, groups=2)


def test_independent_sums_weights_and_targets():
    reactions, records = fixture(); flat, names, errors = assemble(reactions, records)
    assert names == ['a', 'b', 'c'] and max(errors.values()) < 1e-12
    np.testing.assert_array_equal(flat['fixed_energy'], [3., 2.])
    np.testing.assert_array_equal(flat['target'], [1., 3.])
    np.testing.assert_array_equal(flat['objective_weight'], [10., .5])


@pytest.mark.parametrize('mutation', ['missing', 'extra', 'partial', 'group', 'duplicate', 'nan', 'grid', 'weight'])
def test_reject_invalid_sources(mutation):
    reactions, records = fixture()
    if mutation == 'missing': del records['c']
    if mutation == 'extra': records['d'] = records['c']
    if mutation == 'partial': reactions.pop()
    if mutation == 'group': reactions[1]['set_or_subset'] = 'g1'
    if mutation == 'duplicate': reactions[1]['reaction'] = 'r1'
    if mutation == 'nan': records['a'][0][0] = np.nan
    if mutation == 'grid': records['a'][2]['99590'][291] = 1.
    if mutation == 'weight': reactions[0]['objective_weight'] = 0.
    with pytest.raises((ValueError, FloatingPointError)):
        assemble(reactions, records)


def test_exact_pilot_row_mapping_and_change_rejected():
    reactions, records = fixture(); flat, _, _ = assemble(reactions, records)
    subset = {k: v[[1, 0]] for k, v in flat.items()}
    assert a.check_pilot(flat, reactions, subset, reactions[::-1]) == [1, 0]
    subset['target'][0] += 1e-12
    with pytest.raises(AssertionError): a.check_pilot(flat, reactions, subset, reactions[::-1])


def test_refuses_overwrite_before_reading_sources(tmp_path):
    with pytest.raises(ValueError, match='preserve existing'):
        a.publish(tmp_path)
