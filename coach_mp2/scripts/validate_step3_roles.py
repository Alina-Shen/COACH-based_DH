"""Independent semantic/readback validation of the solver-neutral Step 3 snapshot."""
from pathlib import Path
import csv,json,math,hashlib
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'manifests/data_roles_v1'
ROLES=['coefficient_fitting','model_selection','overfitting_diagnostic','final_assessment']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rows(p):
 with Path(p).open(newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))
def flag(r,k):
 if r[k] not in ['True','False']:raise ValueError('Invalid boolean')
 return r[k]=='True'
def audit(data=DATA,check_sources=True):
 checks={}
 def check(k,v):
  checks[k]=bool(v)
  if not v:raise ValueError(k)
 policy=json.loads((data/'policy.json').read_text());provenance=json.loads((data/'provenance.json').read_text())
 if check_sources:
  check('source_hashes',all(sha(p)==h for p,h in provenance['sources'].items()))
 core=rows(data/'source/DatasetEval.csv');raw=core+rows(data/'source/BigNC_DatasetEval.csv')+rows(data/'source/GDB9-W1-F12_DatasetEval.csv')
 reactions=rows(data/'reactions.csv');species=rows(data/'species.csv');datasets=rows(data/'datasets.csv')
 check('reaction_count_and_unique',len(reactions)==11839 and len({r['reaction'] for r in reactions})==11839)
 check('source_row_order_stoichiometry_and_references',[(r['reaction'],r['dataset'],r['reference_hartree'],r['stoichiometry']) for r in reactions]==[(r['Reaction'],r['Dataset'],r['Reference'],r['Stoichiometry']) for r in raw])
 check('indices_exact',all(int(r['index'])==i for i,r in enumerate(reactions)))
 if check_sources:
  ref=ROOT.parent/'revwb97m2/manifests/data_roles'
  check('species_order_identical_reference',[r['species'] for r in species]==[r['species'] for r in rows(ref/'species_roles.csv')])
  check('dataset_order_identical_reference',[r['dataset'] for r in datasets]==[r['dataset'] for r in rows(ref/'dataset_roles.csv')])
 standard=rows(data/'source/Standard_errors.csv');core_sets={r['Dataset'] for r in standard};check('137_core_datasets',len(core_sets)==137)
 entries=rows(data/'source/coach_si_table2_final_cycle_entries.csv');fit={r['reaction']:float(r['objective_weight']) for r in entries}
 check('1498_unique_fitting_entries',len(entries)==len(fit)==1498)
 check('fit_global_order',all(int(r['global_index'])==i+1 for i,r in enumerate(entries)))
 transcription=json.loads((data/'source/weight_transcription.json').read_text());expanded=[]
 for sr in transcription['rows']:
  members=[r['Reaction'] for r in core if r['Dataset']==sr['dataset_eval_dataset']]
  chosen=members if sr['selection']=='all' else [sr['reaction_id_template'].format(index=i) for i in sr['selection']]
  check('SI count '+sr['set_or_subset'],len(chosen)==sr['count'] and len(set(chosen))==len(chosen) and set(chosen)<=set(members))
  expanded.extend((r,1/math.sqrt(j) if sr['weight']=='1/sqrt(j)' else float(sr['weight'])) for j,r in enumerate(chosen,1))
 check('SI_expansion_exact_order_and_weight',expanded==[(r['reaction'],float(r['objective_weight'])) for r in entries])
 sets={k:set() for k in ROLES};counts={k:0 for k in ROLES};allsp=set()
 finals={'SC74','OEEFD','L14','vL11','GDB_W1-F12'}
 for r in reactions:
  actual=[flag(r,k) for k in ROLES];expected=[r['reaction'] in fit,r['dataset'] in core_sets,r['dataset'] in {'AE11','MB08-165','MB16-43'},r['dataset'] in finals]
  if actual!=expected:raise ValueError('role mismatch '+r['reaction'])
  if (float(r['objective_weight']) if r['objective_weight'] else None)!=fit.get(r['reaction']):raise ValueError('weight mismatch')
  fields=r['stoichiometry'].split(',');check_name='valid_stoichiometry'
  if len(fields)%2 or not all(math.isfinite(float(x)) and float(x)!=0 for x in fields[::2]):raise ValueError(check_name)
  members=set(fields[1::2]);allsp.update(members)
  for k,b in zip(ROLES,actual):
   if b:sets[k].update(members);counts[k]+=1
 check('all_row_roles_and_weights',True)
 check('energy_species_unique_union',len(species)==len({r['species'] for r in species})==len(allsp)==17452 and {r['species'] for r in species}==allsp)
 check('species_membership',all(flag(r,k)==(r['species'] in sets[k]) for r in species for k in ROLES))
 expected_counts=[(1498,2799),(8377,13907),(219,249),(3462,3573)]
 for k,(nr,ns) in zip(ROLES,expected_counts):check(k+'_counts',counts[k]==nr and len(sets[k])==ns and policy['counts'][k]=={'reactions':nr,'species':ns})
 if check_sources:
  metadata_sets={g:set(json.loads(Path(p).read_text())) for g,p in policy['metadata_sources'].items()}
  check('current_database_metadata_membership',set.union(*metadata_sets.values())==allsp|set(policy['excluded_OPT']) and metadata_sets['OPT']==set(policy['excluded_OPT']))
 check('OPT_excluded',len(policy['excluded_OPT'])==206 and not set(policy['excluded_OPT'])&allsp and policy['metadata_count']==17658)
 check('dataset_membership',len(datasets)==142 and {r['dataset'] for r in datasets}==core_sets|finals)
 for d in datasets:
  rr=[r for r in reactions if r['dataset']==d['dataset']]
  if int(d['reaction_count'])!=len(rr) or any(int(d[k])!=sum(flag(r,k) for r in rr) for k in ROLES):raise ValueError('Dataset aggregation mismatch')
 check('dataset_counts',True)
 for i,a in enumerate(ROLES):
  for b in ROLES[i+1:]:check('overlap_'+a+'_'+b,policy['overlap'][a+'__'+b]==dict(reactions=sum(flag(r,a) and flag(r,b) for r in reactions),species=len(sets[a]&sets[b])))
 check('no_final_reaction_leakage',all(not(flag(r,'final_assessment') and (flag(r,'model_selection') or flag(r,'coefficient_fitting'))) for r in reactions))
 check('solver_neutral',policy['solver_neutral'] is True)
 check('standard_denominators',all(math.isfinite(r['standard_metric']) and r['standard_metric']>0 and r['standard_metric']==float(next(s['Metric'] for s in standard if s['Dataset']==r['dataset'])) for r in policy['metrics']['datasets']))
 return dict(passed=True,checks=checks,counts=policy['counts'],overlap=policy['overlap'],solver_choice_required=False)
def main():
 report=audit();freeze=ROOT/'manifests/step3_freeze_v1.json'
 if freeze.exists():
  pins=json.loads(freeze.read_text())['sha256'];report['freeze_hashes_pass']=all(sha(ROOT/p)==h for p,h in pins.items())
  if not report['freeze_hashes_pass']:raise ValueError('Frozen artifact changed')
 (ROOT/'results/step3_roles_validation.json').write_text(json.dumps(report,indent=2)+'\n')
 print('Step3 PASS',len(report['checks']),'semantic checks; frozen hashes',report.get('freeze_hashes_pass','not frozen yet'))
if __name__=='__main__':main()
