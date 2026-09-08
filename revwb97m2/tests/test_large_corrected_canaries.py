import pytest
from revwb97m2.scripts import run_large_corrected_canaries as launch


def test_large_scope_and_allocation():
    plan = {'cases':[{'species':'BSR36_c4','resources':{'cpus':16,'requested_memory_gib':227}}]}
    assert launch.require_case(plan,'BSR36_c4',16,227)['species']=='BSR36_c4'
    with pytest.raises(ValueError):
        launch.require_case(plan,'TMD01_H',16,227)
    with pytest.raises(ValueError):
        launch.require_case(plan,'BSR36_c4',16,14)


def test_invalid_contract_prevents_run(monkeypatch):
    def fail():
        raise ValueError('checkpoint changed')
    monkeypatch.setattr(launch,'load',fail)
    with pytest.raises(ValueError,match='checkpoint changed'):
        launch.run('BSR36_c4',16,227)
