"""Audit native pilot without equating job completion with chemical validation."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
OUT=Path('/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2/step2_pilot_v1')
rows=[]
for species in ['SIE4x4_h2o','16_C_AE18']:
 ref=ROOT.parent/'coach/FunctionalCOACH/tests/qchem_outputs'/f'{species}.out'
 target=float(re.search(r'SCF\s+energy in the final basis set\s*=\s*([-\d.]+)',ref.read_text())[1])
 for mode in ['fixed','scf']:
  p=OUT/f'{species}_{mode}.out';text=p.read_text() if p.exists() else ''
  cycles=re.findall(r'^\s*(\d+)\s+(-\d+\.\d+)\s+([\d.Ee+-]+)\s+(.+)$',text,re.M)
  cycles=[c for c in cycles if 'step' in c[3] or 'Convergence criterion met' in c[3]]
  done='Thank you very much for using Q-Chem' in text
  converged=[c for c in cycles if 'Convergence criterion met' in c[3]]
  row=dict(species=species,mode=mode,output=str(p),sha256=hashlib.sha256(text.encode()).hexdigest(),normal_termination=done,reference_hartree=target,reference_source=str(ref),reference_scope='COACH regression fixture; not GSCDB Analysis',cycle_count=len(cycles),converged=bool(converged))
  if mode=='fixed':row.update(skip_scf='Skip SCF calculation as requested' in text,energy_reconstruction_pass=False,limitation='GEN_SCFMAN TRUE / MAX_SCF_CYCLES 0 skips energy evaluation in this build; normal termination is only a native scratch-read check.')
  if cycles:row.update(first_cycle_hartree=float(cycles[0][1]),first_cycle_minus_reference_hartree=float(cycles[0][1])-target)
  if converged:
   energy=float(converged[-1][1]);row.update(converged_hartree=energy,difference_hartree=energy-target,tolerance_hartree=2e-6,repeatability_pass=done and abs(energy-target)<2e-6)
  rows.append(row)
report=dict(job_id='25820274',cases=rows,step2_complete=False,remaining=['COACH Analysis reference location unresolved.','Dedicated zero-update energy reconstruction remains unverified; skip-SCF mode provides no energy.','Exact historical source build unknown; current reproduction runtime is hashed.'])
workbook_report=ROOT/'results/step2_workbook_reference_v1.json'
if workbook_report.exists():
 report['workbook_reference_report']=str(workbook_report)
 report['reference_location_resolved']=True
 report['remaining']=[r for r in report['remaining'] if 'reference location unresolved' not in r]
(ROOT/'results/step2_pilot_v1.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
