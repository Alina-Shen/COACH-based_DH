"""Explicit pending-only migration and persistent globally bounded admission."""
import argparse
from datetime import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
from .adapter import DATA, ROOT, checked_authorization
from .leases import Ledger, occupied
from .policy import dependency, ROUTES
from .smoke import sources

DISCOVERY = '25801134'
SELECTED = '25802824'
BUILD = '25802822'
GRID = '25802823'
SCRIPT = ROOT/'revwb97m2/multipartition_v1'
TERMINAL = {'COMPLETED','CANCELLED','FAILED','TIMEOUT','OUT_OF_MEMORY','NODE_FAIL','PREEMPTED','BOOT_FAIL'}


def cmd(*args):
    return subprocess.check_output(args, text=True, timeout=60).strip()


def queue():
    rows = cmd('squeue','-r','-u','yaoshen','-h','-o','%i|%T|%j|%P|%R')
    return {r[0]: dict(state=r[1], name=r[2], partition=r[3], reason=r[4])
            for r in (line.split('|') for line in rows.splitlines()) if len(r)==5}


def accounting(job):
    rows = cmd('sacct','-X','-j',job,'-n','-P','--format=JobID,State,ExitCode,End')
    result = {}
    for line in rows.splitlines():
        parts = line.split('|')
        if len(parts)>=4:
            result[parts[0]] = dict(state=parts[1].split()[0], exit=parts[2], end=parts[3])
    return result


def write(path, value):
    temp = path.with_suffix('.tmp')
    with temp.open('w') as stream:
        json.dump(value, stream, indent=2)
        stream.flush(); os.fsync(stream.fileno())
    os.replace(temp,path)


def event(root, **data):
    data['time'] = datetime.now().isoformat()
    with (root/'events.jsonl').open('a') as stream:
        stream.write(json.dumps(data)+'\n'); stream.flush(); os.fsync(stream.fileno())
    print(json.dumps(data), flush=True)


def scoped(q, job, name):
    if job not in q or q[job]['name'] != name or q[job]['state'] != 'PENDING':
        raise ValueError('not an exact pending target: '+job)


def successful(job, live):
    if job in live: return False
    row = accounting(job).get(job)
    if row is None: return False
    if row['state']=='COMPLETED' and row['exit']=='0:0': return True
    if row['state'] in TERMINAL: raise RuntimeError('required job failed: '+job+' '+row['state'])
    return False


def compute_gate(smoke_job, live):
    if not successful(smoke_job,live): raise ValueError('smoke not complete')
    from revwb97m2 import discovery_extension_v1 as e
    from .smoke_model import readback
    checkroot=DATA/'dispatch/activation_checks_v1'/smoke_job
    reports=[json.loads((checkroot/str(i)/'passed.json').read_text()) for i in (0,1)]
    if (not all(r['passed'] and r['real_adapter_readback'] and r['cross_node_capacity']==20 for r in reports)
            or reports[0]['host']==reports[1]['host']):
        raise ValueError('activation compute gate failed')
    if len(json.loads((checkroot/'shared_lock_test/leases.json').read_text()))!=20:
        raise ValueError('shared lock state inconsistent')
    p,_,graph,_=e.check(ROOT/'revwb97m2/manifests/discovery_extension_v1/release_20260911.json')
    arrays,ids,settings=e.old.load_data()
    for i in (0,1):
        auth=json.loads((checkroot/str(i)/'authorization.json').read_text())
        if auth['source_hashes']!=sources(): raise ValueError('smoke code differs from activation code')
        readback(e.old,{**p['additional_tasks'][0],'seconds':120},Path(auth['smoke_root']),
                 graph,arrays,ids,settings,__import__('numpy').array([],dtype=int))
    return reports


def activate(root, smoke_job, baseline_confirmed=False):
    if not baseline_confirmed:
        raise ValueError('Gurobi baseline20 must be confirmed for the exact license file before activation')
    if DATA/'dispatch' not in root.resolve().parents:
        raise ValueError('out-of-scope state root')
    if root.exists(): raise ValueError('state root exists; inspect before resuming')
    live = queue()
    reports=compute_gate(smoke_job,live)
    for job,name in ((BUILD,'r2_selected_build'),(GRID,'r2_selected_full')):
        scoped(live,job,name)
    pending=[k for k,v in live.items() if k.startswith(DISCOVERY+'_') and v['state']=='PENDING']
    selected=[k for k,v in live.items() if k.startswith(SELECTED+'_')]
    if not pending or len(selected)!=414: raise ValueError('unexpected migration inventory')
    for job in pending: scoped(live,job,'r2_discovery_ext')
    for job in selected: scoped(live,job,'r2_selected_full')
    root.mkdir(parents=True)
    state=dict(stage='preparing', smoke_job=smoke_job, before=live, jobs=[], legacy=[],
               controller_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    write(root/'state.json',state)
    # Protect descendants before changing/cancelling their dependency parents.
    for job in (BUILD,GRID,SELECTED):
        cmd('scontrol','hold',job); event(root,action='hold',job=job)
    for job in pending:
        now=queue()
        if job in now and now[job]['state']=='PENDING': cmd('scontrol','hold',job)
    live=queue()
    pending=[k for k,v in live.items() if k.startswith(DISCOVERY+'_') and v['state']=='PENDING']
    for job in pending:
        scoped(live,job,'r2_discovery_ext')
        if live[job]['reason']!='(JobHeldUser)': raise ValueError('pending task not securely held: '+job)
    indices=sorted(int(j.split('_')[1]) for j in pending)
    if not indices: raise ValueError('no pending discovery remains')
    from revwb97m2 import discovery_extension_v1 as e
    p,_,_,_=e.check(ROOT/'revwb97m2/manifests/discovery_extension_v1/release_20260911.json')
    for index in indices:
        task=p['additional_tasks'][index]['id']
        if (Path(p['output_root'])/(task+'.execution.json')).exists() or (Path(p['output_root'])/task).exists():
            raise ValueError('replacement output already exists: '+task)
    legacy=[j for j,v in live.items() if j.startswith(DISCOVERY+'_') and v['state']!='PENDING']
    ledger=Ledger(root/'ledger')
    ledger.seed_legacy(['legacy:'+j for j in legacy])
    # Account for recent legacy tokens even if their scheduler jobs have ended.
    for job,row in accounting(DISCOVERY).items():
        if '_' not in job or job in legacy or row['state'] not in TERMINAL: continue
        try: ended=datetime.fromisoformat(row['end']).timestamp()
        except ValueError: continue
        if time.time()-ended < 3600:
            owner='retired:'+job
            if not ledger.acquire(owner): raise ValueError('too many legacy token reservations')
            with ledger.transaction() as data:
                data[owner]['cooldown']=3600; data[owner]['closed']=ended
    for i,r in enumerate(reports):
        if time.time()-r['closed_epoch']<330:
            owner='probe:'+str(i)
            if not ledger.acquire(owner): raise ValueError('probe headroom unavailable')
            ledger.close(owner,now=r['closed_epoch'])
    auth=dict(released=True, capacity=20, baseline_confirmed=True, migration_verified=False, ledger_initialized=True,
        require_reserved_lease=True, indices={'discovery':indices,'selected':list(range(414))},
        source_hashes=sources(), ledger=str(root/'ledger'), receipts=str(root/'receipts'),
        discovery_gate=str(root/'discovery_gate.json'))
    write(root/'authorization.json',auth)
    state.update(legacy=legacy, pending_originals=pending, indices=indices)
    write(root/'state.json',state)
    # Replacement arrays start HELD. lr8 validated by this activation's real smoke.
    state['selected_arrays']=[]
    for phase,all_ids in auth['indices'].items():
        for offset in range(0,len(all_ids),200):
            ids=all_ids[offset:offset+200]
            if len(queue())+len(ids)>=999: raise RuntimeError('temporary queue limit would be exceeded')
            job=cmd('sbatch','--parsable','--hold','--array='+','.join(map(str,ids)),
                '--partition=lr8','--account=lr_mhg2','--qos=mhg2_lr8_normal',
                str(SCRIPT/'run.sh'),'--authorization',str(root/'authorization.json'),'--phase',phase).split(';')[0]
            if phase=='discovery': state['discovery_array']=job
            else: state['selected_arrays'].append(job)
            for index in ids: state['jobs'].append(dict(job=job+'_'+str(index),phase=phase,index=index,released=False))
            write(root/'state.json',state); event(root,action='submit_held_array',job=job,phase=phase,count=len(ids))
            if phase=='selected':
                # Selected jobs are leaves. Replace in chunks to stay below999
                # even while old/new pending tasks briefly coexist.
                old_ids=[SELECTED+'_'+str(i) for i in ids]
                now=queue()
                for old_job in old_ids: scoped(now,old_job,'r2_selected_full')
                cmd('scancel','--state=PENDING',*old_ids)
                event(root,action='cancel_replaced_selected_leaves',jobs=old_ids,replacement=job)
    audit=cmd('sbatch','--parsable','--hold','--dependency='+dependency('audit',terminal_jobs=[DISCOVERY,state['discovery_array']]),
        str(SCRIPT/'audit_job.sh'),'--authorization',str(root/'authorization.json'),
        '--output',str(root/'discovery_gate.json')).split(';')[0]
    state['audit']=audit; write(root/'state.json',state)
    dependencies=[(BUILD,dependency('build',validated=audit)),
                  (GRID,dependency('grid',validated=audit,build=BUILD))]
    dependencies += [(j,dependency('selected',validated=audit,build=BUILD,grid=GRID)) for j in state['selected_arrays']]
    for job,dep in dependencies:
        cmd('scontrol','update','JobId='+job,'Dependency='+dep)
        event(root,action='dependency',job=job,dependency=dep)
    # Held targets cannot race to RUNNING; state filter is an additional guard.
    now=queue()
    for job in pending: scoped(now,job,'r2_discovery_ext')
    cmd('scancel','--state=PENDING',*pending)
    event(root,action='cancel_replaced_discovery_pending_only',jobs=pending)
    now=queue()
    if any(j in now and now[j]['state'] not in ('CANCELLED','COMPLETING') for j in pending+selected):
        raise RuntimeError('original cancellation not confirmed; replacements remain held')
    auth['migration_verified']=True; write(root/'authorization.json',auth)
    checked_authorization(root/'authorization.json')
    state['stage']='discovery'; write(root/'state.json',state)
    cmd('scontrol','release',audit)
    event(root,action='migration_verified',discovery=state['discovery_array'],selected=state['selected_arrays'],audit=audit)


def monitor(root, once=False):
    with (root/'controller.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        while True:
            state=json.loads((root/'state.json').read_text())
            if state['controller_sha256']!=hashlib.sha256(Path(__file__).read_bytes()).hexdigest():
                raise RuntimeError('controller source changed')
            auth=checked_authorization(root/'authorization.json')
            ledger=Ledger(auth['ledger']); live=queue()
            if len(live)>=998: raise RuntimeError('user queue limit reached; stop admission')
            for job in state['legacy']:
                owner='legacy:'+job
                if ledger.snapshot()[owner]['closed'] is None and job not in live:
                    rows=accounting(job)
                    if rows.get(job,{}).get('state') in TERMINAL: ledger.close(owner)
            # Reconcile only our new jobs, never other projects or running jobs.
            for task in state['jobs']:
                if not task['released'] or task.get('done'): continue
                job=task['job']; owner=job+':'+task['phase']+':'+str(task['index'])
                if job not in live:
                    rows=accounting(job); row=rows.get(job)
                    if row and row['state'] in TERMINAL:
                        if ledger.snapshot()[owner]['closed'] is None: ledger.close(owner)
                        if row['state']!='COMPLETED' or row['exit']!='0:0':
                            raise RuntimeError('fit failed; admissions stopped: '+job)
                        task['done']=True
            if state['stage']=='discovery' and successful(state['audit'],live): state['stage']='build'
            if state['stage']=='build':
                if not state.get('build_released'):
                    if ledger.acquire('build:'+BUILD,reserved=True):
                        with ledger.transaction() as data: data['build:'+BUILD]['cooldown']=3600
                        scoped(live,BUILD,'r2_selected_build'); cmd('scontrol','release',BUILD)
                        state['build_released']=True
                elif successful(BUILD,live):
                    ledger.close('build:'+BUILD); state['stage']='grid'
                    scoped(live,GRID,'r2_selected_full'); cmd('scontrol','release',GRID)
            if state['stage']=='grid' and successful(GRID,live): state['stage']='selected'
            if state['stage'] in ('discovery','selected'):
                for task in state['jobs']:
                    if task['phase']!=state['stage'] or task['released']: continue
                    job=task['job']; owner=job+':'+task['phase']+':'+str(task['index'])
                    scoped(live,job,'r2_multi_fit')
                    existing=ledger.snapshot().get(owner)
                    if existing is None and not ledger.acquire(owner,reserved=True): break
                    if existing is not None and not existing.get('reserved'): raise RuntimeError('unexpected reservation state')
                    # Persist release intent before mutation; retries remain inspectable.
                    event(root,action='release_reserved',job=job,owner=owner)
                    cmd('scontrol','release',job); task['released']=True
                    write(root/'state.json',state)
            if all(t.get('done') for t in state['jobs']): state['stage']='fits_finished_review_pending'
            write(root/'state.json',state)
            leases=ledger.snapshot()
            event(root,action='status',stage=state['stage'],occupied=sum(occupied(r,time.time()) for r in leases.values()),
                  released=sum(t['released'] for t in state['jobs']),done=sum(bool(t.get('done')) for t in state['jobs']))
            if once or state['stage']=='fits_finished_review_pending': return
            time.sleep(45)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=['activate','monitor','once'])
    p.add_argument('--root',type=Path,required=True); p.add_argument('--smoke-job')
    p.add_argument('--baseline-confirmed',action='store_true',help='Only after Support/dashboard confirms baseline20 for the license in use')
    a=p.parse_args()
    if a.action=='activate': activate(a.root,a.smoke_job,a.baseline_confirmed)
    else: monitor(a.root,once=a.action=='once')
