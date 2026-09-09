import numpy as np
import pytest
from revwb97m2.scripts.refresh_water_scalar_v1 import updated_vector


def test_only_vv10_changes():
    old=np.arange(292,dtype=float)
    new=updated_vector(old,dict(short_range_hf_hartree=old[288],pt2_total_hartree=old[290],vv10_hartree=-0.1))
    keep=np.arange(292)!=289
    assert np.array_equal(new[keep],old[keep]) and new[289]==-0.1
    assert old[289]==289


@pytest.mark.parametrize('key,value', [('short_range_hf_hartree',1),('pt2_total_hartree',1),('vv10_hartree',float('nan'))])
def test_invalid_reuse_rejected(key,value):
    values=dict(short_range_hf_hartree=0,pt2_total_hartree=0,vv10_hartree=0)
    values[key]=value
    with pytest.raises(ValueError):
        updated_vector(np.zeros(292),values)
