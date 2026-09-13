"""Create a project-local solver-neutral role/metric snapshot; never mutate references."""
from pathlib import Path
import csv,json,hashlib,math,shutil
import yaml
ROOT=Path(__file__).resolve().parents[1]
REF=ROOT.parent/'revwb97m2'
DB=Path('/clusterfs/mhg-data/yaoshen/GSCDB')
DEST=ROOT/'manifests/data_roles_v1'
ROLES=['coefficient_fitting','model_selection','overfitting_diagnostic','final_assessment']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rows(p):
 with Path(p).open(newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))
def writecsv(p,data):
 with p.open('x',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
def terms(s):
 fields=s.split(',')
 if len(fields)%2:raise ValueError('Odd stoichiometry')
 result=[]
 for a,b in zip(fields[::2],fields[1::2]):
  x=float(a)
  if not math.isfinite(x) or x==0 or not b:raise ValueError('Invalid stoichiometry')
  result.append((x,b))
 return result
def main():
 if DEST.exists():raise FileExistsError('Version already exists; never overwrite')
 sources={}
 for n in ['DatasetEval.csv','Datasets.csv','Standard_errors.csv','DatasetEval_TMC34_weight.csv','DatasetEval_O24x5_weight.csv']:
  p=DB/'Info'/n;assert sha(p)==sha(REF/'manifests/gscdb137/source'/n);sources[n]=p
 for group in ['BigNC','GDB9-W1-F12']:
  p=DB/'AdditionalSets'/group/'DatasetEval.csv';pinned=Path('/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/authoritative_inputs/qchem/additionalsets_gscdb_8f2c7e5')/group/'DatasetEval.csv';assert sha(p)==sha(pinned);sources[group+'_DatasetEval.csv']=p
 for n in ['coach_si_table2_final_cycle_entries.csv','coach_si_table2_final_cycle_training_weights.csv','coach_si_table2_final_cycle.yaml']:
  sources[n]=REF/'manifests/weights'/n
 source=yaml.safe_load(sources['coach_si_table2_final_cycle.yaml'].read_text())
 paper=ROOT.parent/'coach/paper/SI_COACH_2026MHG.pdf';assert sha(paper)==source['source']['sha256']
 core=rows(sources['DatasetEval.csv']);allrows=core+rows(sources['BigNC_DatasetEval.csv'])+rows(sources['GDB9-W1-F12_DatasetEval.csv'])
 if len({r['Reaction'] for r in allrows})!=len(allrows):raise ValueError('Duplicate reaction')
 grouped={}
 for r in core:grouped.setdefault(r['Dataset'],[]).append(r['Reaction'])
 expanded=[]
 for sr in source['rows']:
  selected=grouped[sr['dataset_eval_dataset']] if sr['selection']=='all' else [sr['reaction_id_template'].format(index=i) for i in sr['selection']]
  assert len(selected)==sr['count']
  for j,r in enumerate(selected,1):
   assert r in grouped[sr['dataset_eval_dataset']]
   expanded.append((r,1/math.sqrt(j) if sr['weight']=='1/sqrt(j)' else float(sr['weight'])))
 entries=rows(sources['coach_si_table2_final_cycle_entries.csv'])
 assert [(r['reaction'],float(r['objective_weight'])) for r in entries]==expanded
 assert len(expanded)==1498 and len(dict(expanded))==1498
 fitting=dict(expanded);standards=rows(sources['Standard_errors.csv']);core_sets={r['Dataset'] for r in standards};assert len(core_sets)==137
 final={'SC74','OEEFD','L14','vL11','GDB_W1-F12'};over={'AE11','MB08-165','MB16-43'}
 reactions=[];species={}
 for i,r in enumerate(allrows):
  dataset=r['Dataset'];name=r['Reaction'];assert dataset in core_sets|final
  flags=[name in fitting,dataset in core_sets,dataset in over,dataset in final]
  record=dict(index=i,reaction=name,dataset=dataset,reference_hartree=r['Reference'],stoichiometry=r['Stoichiometry'],**dict(zip(ROLES,flags)),objective_weight=fitting.get(name,''))
  reactions.append(record)
  for _,sp in terms(r['Stoichiometry']):
   previous=species.setdefault(sp,[False]*4)
   for j,flag in enumerate(flags):previous[j]=previous[j] or flag
 sr=[dict(species=s,**dict(zip(ROLES,flags))) for s,flags in sorted(species.items())]
 # Compare every role and weight with the implemented reference, not just totals.
 prior=rows(REF/'manifests/data_roles/reaction_roles.csv');assert len(prior)==len(reactions)
 for a,b in zip(reactions,prior):
  assert a['reaction']==b['reaction'] and a['dataset']==b['dataset']
  for k in ROLES:assert a[k]==(b[k]=='true')
  assert a['objective_weight']==(float(b['objective_weight']) if b['objective_weight'] else '')
 bysp={r['species']:r for r in rows(REF/'manifests/data_roles/species_roles.csv')};assert set(bysp)==set(species)
 for r in sr:
  for k in ROLES:assert r[k]==(bysp[r['species']][k]=='true')
 sr=[dict(species=name,**dict(zip(ROLES,species[name]))) for name in bysp]
 categories={r['Name']:r['Datatype_Short'] for r in rows(sources['Datasets.csv']) if r['Name']}
 weights={}
 for filename in ['DatasetEval_TMC34_weight.csv','DatasetEval_O24x5_weight.csv']:
  for r in rows(sources[filename]):weights.setdefault(r['Dataset'],[]).append(r)
 metric_rows=[]
 for s in standards:
  ds=s['Dataset'];kind='MAE';offset=0.;w={}
  if ds in {'Pol130','HR46','T144','OEEF'}:kind='MARE'
  if ds=='Dip146':kind='regularized_MAE'
  if ds in weights:
   kind='weighted_absolute_sum';wr=weights[ds]
   if ds in {'TMD10','MOR13','TMB11'}:
    assert wr[-1]['Reaction']==ds+'_residule';offset=float(wr[-1]['Weight']);wr=wr[:-1]
   w={r['Reaction']:float(r['Weight']) for r in wr};assert set(w)==set(grouped[ds])
  metric_rows.append(dict(dataset=ds,category=categories[ds],kind=kind,standard_metric=float(s['Metric']),offset=offset,weights=w))
 counts={role:dict(reactions=sum(r[role] for r in reactions),species=sum(r[role] for r in sr)) for role in ROLES}
 assert counts==dict(zip(ROLES,[{'reactions':1498,'species':2799},{'reactions':8377,'species':13907},{'reactions':219,'species':249},{'reactions':3462,'species':3573}]))
 assert len(sr)==17452
 metadata=rows(REF/'manifests/data_roles/qchem_input_metadata.csv')
 # Step 4 reparses actual input chemistry; Step 3 checks metadata membership only.
 meta_names={r['species'] for r in metadata};assert len(metadata)==17658 and set(species)<=meta_names
 opt=sorted(meta_names-set(species));assert len(opt)==206
 metadata_sources={'GSCDB':DB/'Allmols_info.json',**{g:DB/'AdditionalSets'/g/'Allmols_info.json' for g in ['BigNC','GDB9-W1-F12','OPT']}}
 metadata_sets={g:set(json.loads(p.read_text())) for g,p in metadata_sources.items()}
 assert set.union(*metadata_sets.values())==meta_names and metadata_sets['OPT']==set(opt)
 overlap={a+'__'+b:dict(reactions=sum(r[a] and r[b] for r in reactions),species=sum(r[a] and r[b] for r in sr)) for i,a in enumerate(ROLES) for b in ROLES[i+1:]}
 assert overlap['coefficient_fitting__final_assessment']['reactions']==0
 assert overlap['model_selection__final_assessment']['reactions']==0
 DEST.mkdir();(DEST/'source').mkdir()
 for name,path in sources.items():shutil.copyfile(path,DEST/'source'/name)
 writecsv(DEST/'reactions.csv',reactions);writecsv(DEST/'species.csv',sr)
 datasets=[]
 for ds in [r['dataset'] for r in rows(REF/'manifests/data_roles/dataset_roles.csv')]:
  rs=[r for r in reactions if r['dataset']==ds]
  datasets.append(dict(dataset=ds,**{k:sum(r[k] for r in rs) for k in ROLES},reaction_count=len(rs)))
 writecsv(DEST/'datasets.csv',datasets)
 policy=dict(metadata_sources={g:str(p) for g,p in metadata_sources.items()},schema_version=1,project='coach_mp2',step=3,solver_neutral=True,counts=counts,energy_species_union=len(sr),metadata_count=len(metadata),excluded_OPT=opt,overlap=overlap,
   species_and_dataset_order='identical to pinned revwb97m2 species_roles.csv and dataset_roles.csv',fitting_order='source/coach_si_table2_final_cycle_entries.csv global_index',reaction_order='core DatasetEval then BigNC then GDB9-W1-F12, each in source order',
   fitting_objective='sum(w*r_hartree^2); multiply rows/residual by sqrt(w), not w',final_gate='final-only rows cannot enter fitting/model choice; evaluate after model and K freeze',
   intentional_overlap='fitting overlaps model selection; MB16-43 overlaps diagnostic; neither is an independent holdout',
   bignc_caveat='Original COACH tuned D4-ATM on BigNC; preserve inherited exposure disclosure',input_chemistry_validation='Step4; metadata role membership here does not certify inputs or orbitals',
   metric_input='physical property values in benchmark reporting units, after dataset-specific property transformations; Step13 owns transforms',
   metrics=dict(datasets=metric_rows,overall='unweighted mean of 137 dataset NERs, not mean of category means',category='unweighted mean of dataset NERs within category',diagnostic='unweighted mean of AE11/MB08-165/MB16-43 NERs',ner='dataset-specific metric / Standard_errors.Metric',missing='reject missing/duplicate/nonfinite rows; never silently shrink',gdb_final=['MAE','mean_signed_error','population_SD']))
 (DEST/'policy.json').write_text(json.dumps(policy,indent=2)+'\n')
 (DEST/'source/weight_transcription.json').write_text(json.dumps(source,indent=2)+'\n')
 pins=list(metadata_sources.values())+list(sources.values())+[paper,REF/'manifests/data_roles/reaction_roles.csv',REF/'manifests/data_roles/dataset_roles.csv',REF/'manifests/data_roles/species_roles.csv',REF/'manifests/data_roles/qchem_input_metadata.csv',REF/'manifests/data_roles/revwb97m2_data_roles_v2.yaml',DB/'Analysis/analyze.ipynb',ROOT/'configs/scientific_spec_v1.json']
 (DEST/'provenance.json').write_text(json.dumps({'sources':{str(p):sha(p) for p in pins},'input_chemistry_or_orbital_validation':False,'no_solver_or_jobs_used':True},indent=2)+'\n')
 print(json.dumps({'counts':counts,'overlap':overlap,'created':str(DEST)},indent=2))
if __name__=='__main__':main()
