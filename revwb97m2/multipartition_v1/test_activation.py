"""End-to-end scheduler simulation: no real Slurm writes or license access."""
import copy
import json
import time
from pathlib import Path
import pytest
from . import adapter, controller as c
from revwb97m2 import discovery_extension_v1 as e


@pytest.fixture
def simulation(tmp_path,monkeypatch):
    data=tmp_path/'data'; monkeypatch.setattr(c,'DATA',data); monkeypatch.setattr(adapter,'DATA',data)
    probe=data/'dispatch/activation_checks_v1/999'
    for i in (0,1):
        own=probe/str(i); own.mkdir(parents=True)
        (own/'passed.json').write_text(json.dumps(dict(passed=True,real_adapter_readback=True,
            host='node'+str(i),closed_epoch=time.time()-1000)))
    q={}; events=[]; serial=[1000]; maximum=[0]
    def row(name,state='PENDING'):
        return dict(name=name,state=state,partition='cm1',reason='(Dependency)')
    q[c.DISCOVERY+'_0']=row('r2_discovery_ext','RUNNING')
    for i in (1,2): q[c.DISCOVERY+'_'+str(i)]=row('r2_discovery_ext')
    for i in range(414): q[c.SELECTED+'_'+str(i)]=row('r2_selected_full')
    q[c.BUILD]=row('r2_selected_build'); q[c.GRID]=row('r2_selected_full')
    q['25837199']=row('coach_s10_high','RUNNING')
    def queue():
        maximum[0]=max(maximum[0],len(q)); return copy.deepcopy(q)
    monkeypatch.setattr(c,'queue',queue)
    monkeypatch.setattr(c,'accounting',lambda job: {'999':dict(state='COMPLETED',exit='0:0',end='Unknown')} if job=='999' else {})
    monkeypatch.setattr(c,'compute_gate',lambda job,live: [json.loads((probe/str(i)/'passed.json').read_text()) for i in (0,1)])
    monkeypatch.setattr(e,'check',lambda path: (dict(output_root=str(tmp_path/'old'),
        additional_tasks=[{'id':'task'+str(i)} for i in range(124)]),None,None,None))
    def command(*args):
        events.append(args)
        if args[0]=='sbatch':
            serial[0]+=1; job=str(serial[0])
            arr=next((a.split('=',1)[1] for a in args if a.startswith('--array=')),None)
            if arr is None: q[job]=row('r2_multi_audit')
            else:
                for index in arr.split(','): q[job+'_'+index]=row('r2_multi_fit')
            return job
        if args[0]=='scancel':
            assert args[1]=='--state=PENDING'
            for job in args[2:]:
                assert q[job]['state']=='PENDING'; assert not q[job]['name'].startswith('coach_')
                del q[job]
        elif args[:2]==('scontrol','hold'):
            for job in q:
                if job==args[2] or job.startswith(args[2]+'_'):
                    assert q[job]['state']=='PENDING'; q[job]['reason']='(JobHeldUser)'
        elif args[:2]==('scontrol','release'):
            assert q[args[2]]['state']=='PENDING'; q[args[2]]['reason']='(Resources)'
        return ''
    monkeypatch.setattr(c,'cmd',command)
    root=data/'dispatch/campaign'
    return root,q,events,maximum


def test_transactional_pending_replacement(simulation):
    root,q,events,maximum=simulation
    c.activate(root,'999',baseline_confirmed=True)
    state=json.loads((root/'state.json').read_text())
    assert len(state['jobs'])==416 and len(state['selected_arrays'])==3
    assert state['stage']=='discovery' and maximum[0]<999
    assert q[c.DISCOVERY+'_0']['state']=='RUNNING'
    assert q['25837199']['state']=='RUNNING'
    cancelled=[x for x in events if x[0]=='scancel']
    assert sum(len(x)-2 for x in cancelled)==416
    discovery_cancel=next(i for i,x in enumerate(events) if x[0]=='scancel' and c.DISCOVERY+'_1' in x)
    for job in (c.BUILD,c.GRID):
        assert any(x[:2]==('scontrol','update') and 'JobId='+job in x for x in events[:discovery_cancel])
    c.monitor(root,once=True)
    state=json.loads((root/'state.json').read_text())
    assert sum(t['released'] for t in state['jobs'])==2
    assert not any(t['released'] for t in state['jobs'] if t['phase']=='selected')
    leases=json.loads((root/'ledger/leases.json').read_text())
    assert len(leases)==3 and sum(r.get('reserved',False) for r in leases.values())==2


def test_failed_audit_never_releases_selected(simulation,monkeypatch):
    root,q,events,_=simulation
    c.activate(root,'999',baseline_confirmed=True)
    state=json.loads((root/'state.json').read_text()); audit=state['audit']; del q[audit]
    monkeypatch.setattr(c,'accounting',lambda job: {audit:dict(state='FAILED',exit='1:0',end='Unknown')} if job==audit else {})
    count=len(events)
    with pytest.raises(RuntimeError,match='required job failed'): c.monitor(root,once=True)
    assert not any(x[:2]==('scontrol','release') for x in events[count:])


def test_entitlement_confirmation_required_before_any_scheduler_mutation(simulation):
    root,q,events,_=simulation
    with pytest.raises(ValueError,match='baseline20'): c.activate(root,'999')
    assert not events and not root.exists()


@pytest.mark.parametrize('partition', list(c.ROUTES))
def test_explicit_initial_route_for_all_new_submissions(simulation, partition):
    root,q,events,_=simulation
    c.activate(root,'999',baseline_confirmed=True,partition=partition)
    account,qos=c.ROUTES[partition]
    submissions=[args for args in events if args[0]=='sbatch']
    assert len(submissions)==5  # discovery, three selected chunks, scientific audit
    for args in submissions:
        assert '--partition='+partition in args
        assert '--account='+account in args
        assert '--qos='+qos in args
        assert not any('lowprio' in arg for arg in args)
    state=json.loads((root/'state.json').read_text())
    assert state['initial_route']==dict(partition=partition,account=account,qos=qos)
    assert q[c.DISCOVERY+'_0']['state']=='RUNNING'
    assert q['25837199']['state']=='RUNNING'


def test_invalid_initial_route_before_any_scheduler_mutation(simulation):
    root,q,events,_=simulation
    with pytest.raises(ValueError,match='unapproved dispatch partition'):
        c.activate(root,'999',baseline_confirmed=True,partition='lr_lowprio')
    assert not events and not root.exists()
