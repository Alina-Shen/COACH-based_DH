from pathlib import Path
import hashlib
from revwb97m2.scripts import generate_training_features_v3 as g
v=g.native;folder=g.ROOT/'manifests/full_training_execution_v1';summary=v.read(folder/'summary.json')
names=[]
for item in summary['records']:
    path=Path(item['plan']);assert v.digest(path)==item['plan_sha256']
    plan=v.read(path)
    assert not Path(plan['output_root']).exists() and not Path(plan['scratch_root']).exists()
    assert plan['concurrency_proposal'] is None
    for case in plan['cases']:
        names.append(case['species'])
        assert v.canonical_tree_hash(case['source_tree'])==case['source_tree_sha256']
        assert next(f['sha256'] for f in case['source_tree'] if f['path']=='qarchive.h5')==case['qarchive_sha256']
        assert all(hashlib.sha256(stage['input'].encode()).hexdigest()==stage['input_sha256'] for stage in case['stages'].values())
    release=v.read(folder/(item['name']+'_release_draft.json'))
    assert release['user_approved_submission'] is False and release['resource_review_passed'] is False
    assert release['plan_sha256']==v.digest(path)
pilot=set(v.read(Path('/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/matrices/pilot100_v1/species.json')))
reuse=pilot|set(v.read(g.corrected.REGISTRY)['species'])
full=v.read(g.ROOT/'results/training_preflight_v2/full1498_reactions.json')
required={t['species'] for r in full for t in r['stoichiometry']}
assert len(names)==len(set(names))==2569 and not (reuse&set(names))
assert len(reuse)==230 and reuse|set(names)==required and len(required)==2799
free=min(v.available_bytes(v.DATA),v.available_bytes(v.SCRATCH))
assert free>summary['total_minimum_copy_bytes']+557*1024**3
result=dict(passed=True,plans=len(summary['records']),generation_species=len(names),reuse_species=len(reuse),
    full_species=len(required),stages=summary['total_stages'],
    minimum_copy_bytes=summary['total_minimum_copy_bytes'],free_bytes_at_audit=free,
    minimum_copy_tib=summary['total_minimum_copy_bytes']/1024**4,
    all_execution_namespaces_absent=True,all_releases_disabled=True,
    summary_sha256=v.digest(folder/'summary.json'),
    note='Independent cross-manifest coverage, embedded input/tree hashes and headroom checks. Source bytes hashed during freeze; execution rechecks source identity. No jobs/copies.')
v.write(g.ROOT/'results/2026-09-09-full-training-execution-freeze-audit.json',result)
print(result,flush=True)
