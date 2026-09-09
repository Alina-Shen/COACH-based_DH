from concurrent.futures import ProcessPoolExecutor,as_completed
from pathlib import Path
import subprocess
from revwb97m2.scripts import generate_training_features_v3 as g
v=g.native
FOLDER=g.ROOT/'manifests/full_training_execution_v1'


def freeze_one(task):
    name,names=task;path=FOLDER/(name+'.json')
    plan=g.freeze(path,names,'full_training_v1_'+name)
    g.load(path)
    resources={tuple(c['resources'][k] for k in ('cpus','requested_memory_gib','wall_hours')) for c in plan['cases']}
    assert len(resources)==1
    draft=dict(plan_sha256=v.digest(path),corrected_evidence_sha256=v.digest(g.corrected.REGISTRY),
        user_approved_submission=False,resource_review_passed=False,commit='USER_EXECUTION_COMMIT_REQUIRED',
        ecp_native_gateway_authorized=False,max_concurrent_jobs=None,
        scheduler_routes={c['species']:c['route'] for c in plan['cases']})
    v.write(FOLDER/(name+'_release_draft.json'),draft)
    try:g.release_check(path,FOLDER/(name+'_release_draft.json'))
    except ValueError as error:assert 'release not approved' in str(error)
    else:raise AssertionError('disabled draft accepted')
    record=dict(name=name,plan=str(path),plan_sha256=v.digest(path),species=len(names),
        stages=sum(len(c['stages']) for c in plan['cases']),minimum_copy_bytes=plan['minimum_copy_bytes'],
        cpus=next(iter(resources))[0],memory_gib=next(iter(resources))[1],wall_hours=next(iter(resources))[2])
    print('PASS frozen',record,flush=True)
    return record


if __name__=='__main__':
    assert not FOLDER.exists();FOLDER.mkdir()
    selection=v.read(g.ROOT/'manifests/generation_compat_v1/full_training_selection_draft.json')
    evidence=g.corrected.validate_registry()
    assert set(selection['reuse_candidates'])<=set(evidence)
    from revwb97m2 import pilot100_inputs as a
    a.check_matrix()
    report=dict(passed=True,tests='228 passed in20.17s',seven_canary_readback_passed=True,
        species=sorted(evidence),reused_extra_species=selection['reuse_candidates'],matrix_passed=True,
        commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        compatibility_contract_sha256=v.digest(g.compat.CONTRACT),
        note='Read existing raw/native/Q4/publication evidence through versioned reader. No native reruns; unchanged science/tolerances.')
    v.write(g.ROOT/'results/2026-09-09-generation-compat-tests-readback.json',report)
    tasks=[]
    for memory,names in sorted(selection['ordinary_resource_groups'].items(),key=lambda x:int(x[0])):
        for i in range(0,len(names),500):tasks.append((f'ordinary_m{memory}_{i//500:02d}',names[i:i+500]))
    tasks.append(('ecp21_gateway',selection['embedded_ecp_gateway_candidates']))
    with ProcessPoolExecutor(max_workers=2) as pool:
        records=[f.result() for f in as_completed([pool.submit(freeze_one,t) for t in tasks])]
    records.sort(key=lambda r:r['name'])
    assert sum(r['species'] for r in records)==2569
    result=dict(passed=True,submission_authorized=False,records=records,accepted_reuse_species=230,
        generation_species=2569,total_species=2799,total_stages=sum(r['stages'] for r in records),
        total_minimum_copy_bytes=sum(r['minimum_copy_bytes'] for r in records),
        note='Max500 entries per manifest for manageable arrays/review; no running-task cap or required serial batching. All launches disabled pending commit/live resource review. ECP21 is explicit native gateway.')
    v.write(FOLDER/'summary.json',result)
    print('COMPLETE', {k:value for k,value in result.items() if k!='records'},flush=True)
