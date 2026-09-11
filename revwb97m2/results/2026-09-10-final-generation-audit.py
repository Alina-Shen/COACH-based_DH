import sys,json,time,datetime,collections,concurrent.futures
from pathlib import Path
sys.path.insert(0,'/clusterfs/mhg-data/yaoshen/coach-based_dh')
import numpy as np
from revwb97m2.scripts import full_training_feeder_v1 as f,generate_training_features_v3 as g
b=Path('/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/campaigns/full_training_20260909_v1')
dest=Path('/clusterfs/mhg-data/yaoshen/coach-based_dh/revwb97m2/results/2026-09-10-final-generation-audit.json')
f.require(not dest.exists(),'Do not overwrite final audit')
c=f.read(b/'campaign.json');s=f.read(b/'controller/state.json')
f.require(s.get('finished') is True and s['completed']==2569 and not s.get('halted') and not s.get('intent'),'Controller not successfully finished')
q=f.queue();ids=[j['job_id'] for j in s['jobs'] if j['indices']];account={};batch={}
for off in range(0,len(ids),50):
 raw=f.command(['sacct','--array','-j',','.join(ids[off:off+50]),'-nP','--format=JobID%80,State%40,ExitCode,ElapsedRaw,MaxRSS,End'])[0]
 for line in raw.splitlines():
  fields=line.split('|')
  if fields[0].endswith('.batch'):batch[fields[0][:-6]]=fields[1:]
  elif '.' not in fields[0]:account[fields[0]]=fields[1:]
jobs={(j['record'],i):j for j in s['jobs'] for i in j['indices']}
f.require(len(jobs)==sum(len(j['indices']) for j in s['jobs'])==2569,'Duplicate/omitted journal index')
records=[];errors=[];started=time.time();stage_count=0
def audit_case(r,plan,settings,i):
 case=plan['cases'][i];name=case['species'];root=Path(plan['output_root'])/name
 task=f"{jobs[(r['name'],i)]['job_id']}_{i}"
 row=dict(species=name,plan=r['name'],task=task,accounting=account.get(task),batch_accounting=batch.get(task),stages=len(case['stages']))
 try:
  f.require(task not in q and account.get(task,[])[:2]==['COMPLETED','0:0'],'Not COMPLETED/0:0')
  f.publication(r,i)
  f.require(g.native.canonical_tree_hash(g.native.tree_manifest(Path(case['orbital_root'])))==case['source_tree_sha256'],'Original restart tree changed')
  vector,fixed,differences,values=g.corrected.components(root,case,settings)
  g.compare_vectors(np.load(root/'ready/feature_vector_292.npy',allow_pickle=False),vector)
  f.require(f.read(root/'ready/fixed_energy.json')==fixed and f.read(root/'ready/scalar_values.json')==values,'Reconstructed energies differ')
  for grid,difference in differences.items():
   f.require(np.array_equal(np.load(root/f'ready/grid_difference_{grid}.npy',allow_pickle=False),difference),'Reconstructed grid differs')
  f.require(np.isfinite(vector).all() and all(np.isfinite(d).all() for d in differences.values()),'Nonfinite features')
  row.update(passed=True,hf_error=abs(fixed['pure_hf_reconstruction_error_hartree']),pt2_error=abs(values.get('pt2_scaled_identity_error_hartree',0)))
 except Exception as e:row.update(passed=False,error=repr(e))
 return row
for r in c['records']:
 plan,settings=g.load(Path(r['plan']))
 print('Checking',r['name'],len(plan['cases']),flush=True)
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
  for row in pool.map(lambda i:audit_case(r,plan,settings,i),range(len(plan['cases']))):
   records.append(row);stage_count+=row['stages']
   if not row['passed']:errors.append(row);print('FAIL',row,flush=True)
   if len(records)%25==0:print('Progress',len(records),'/2569;errors',len(errors),'seconds',round(time.time()-started),flush=True)
 f.save('/tmp/r2-final-audit-progress.json',dict(checked=len(records),errors=errors,last_plan=r['name'],seconds=time.time()-started))
print('Fresh canary reuse readback',flush=True)
reuse=g.corrected.validate_registry()
selection=f.read(g.ROOT/'manifests/generation_compat_v1/full_training_selection_draft.json')
extra=selection['reuse_candidates'];f.require(len(extra)==6 and set(extra)<=set(reuse),'Missing six reuse species')
result=dict(passed=not errors and len(records)==2569 and stage_count==15412,
 timestamp=datetime.datetime.now().astimezone().isoformat(),seconds=time.time()-started,
 generated_species=len(records),extra_reused_species=extra,total_remainder_species=len(records)+len(extra),
 stages=stage_count,errors=errors,records=records,controller={k:v for k,v in s.items() if k not in ('jobs','migrations')},
 max_hf_error=max((r.get('hf_error',0) for r in records),default=0),max_pt2_error=max((r.get('pt2_error',0) for r in records),default=0),
 audit_scope='ALL generated species: original restart tree hashes, frozen plans/builds/spec/input identities, stage artifacts+working qarchives+saved MOs+electron/spin+normal termination, Q4 native IDV publication, reconstructed292vectors/D4/fixed/scalars/bothgrids; fresh seven-canary readback covers6extra reuse. No newSCF/Qchem or fitter execution.')
f.save(dest,result)
print('FINAL',json.dumps({k:v for k,v in result.items() if k not in ('records','controller')}),flush=True)
