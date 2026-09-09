import copy
import pytest
from revwb97m2.scripts import embedded_y_features_v1 as y


def source(charge=0,mult=2):
    return f'$molecule\n{charge} {mult}\nY 0 0 0\n$end\n$rem\nBASIS GEN\nECP GEN\nPURECART 11111\n$end\n$basis\nY 0\n$end\n$ecp\nY-ECP 4 28\n$end\n'


def bridge(count=11,spin=1):
    return dict(ecp_resolution='embedded_qchem_block',orbital_resolution='embedded_qchem_block',
                ecp_electrons='28',electron_count=str(count),spin=str(spin))


def test_y_valence_counts():
    assert y.electron_count(source(),bridge())==(11,1)
    assert y.electron_count(source(1,1),bridge(10,0))==(10,0)


@pytest.mark.parametrize('text', [source().replace('28','10'),source().replace('11111','1111'),
                               source().replace('ECP GEN','ECP NONE'),source().replace('Y 0 0 0','V 0 0 0')])
def test_changed_representation_rejected(text):
    with pytest.raises(ValueError):y.electron_count(text,bridge())


def test_wrong_bridge_rejected():
    with pytest.raises(ValueError):y.electron_count(source(),bridge(10,0))
