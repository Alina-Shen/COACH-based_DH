"""Freeze Step 8 only after successful numerical validation and parser tests."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 v=json.loads((R/'results/step8_validation.json').read_text());assert v['passed'] and len(v['cases'])==12 and all(c['passed'] for c in v['cases'])
 assert '\nOK\n' in (R/'results/step8_tests.log').read_text()
 h=Path(v['output']);m=json.loads((h/'manifest.json').read_text());assert sha(h/'manifest.json')==v['feature_manifest_sha256'];assert len(m['columns'])==292 and len(m['sha256'])==10
 for f,s in m['sha256'].items():assert sha(h/f)==s
 build=json.loads((R/'manifests/step8_build_v1.json').read_text());assert sha(R/'manifests/step5_no_orientation_build_v1.json')==build['parent_build_manifest_sha256']
 contract=dict(step=8,scope='validated water/carbon pilot; production remains Step12',binary=build['binary'],binary_sha256=build['binary_sha256'],local_libks=build['libks'],local_libks_sha256=build['libks_sha256'],runtime_environment='slurm/run_step8_native.sh',protocol='manifests/step8_protocol_v1.json',omega=.27,selected_rows=[64,154,166],columns=292,features=str(h),fixed_energy='nuclear + one-electron + Coulomb + full LR-HF',scalars=['SRHF','VV10','PT2_total=OS+SS (singles excluded)','D4_ATM'],pt2_authority='configs/step6_runtime_authority_v1.json',carbon_deferral='configs/step6_carbon_accuracy_deferral_v1.json',source_orbitals='immutable Step5 project imports; runtime uses separate scratch copies',solver_required=False)
 (R/'configs/step8_runtime_authority_v1.json').write_text(json.dumps(contract,indent=2)+'\n')
 paths=[]
 for pattern in ['scripts/*step8*.py','scripts/step8_reference/*.py','slurm/run_step8*.sh','inputs/step8_v1/*.in','runtime/step8_source/**/*','manifests/step8_*v1.json','configs/step8_*v1.json','results/step8_validation.json','results/step8_tests.log']:
  paths.extend(p for p in R.glob(pattern) if p.is_file() and p.name!='step8_freeze_v1.json')
 freeze=dict(step=8,sha256={str(p.relative_to(R)):sha(p) for p in sorted(set(paths))},feature_manifest_sha256=v['feature_manifest_sha256'],step6_freeze_sha256=sha(R/'manifests/step6_freeze_v1.json'),step5_build_manifest_sha256=sha(R/'manifests/step5_no_orientation_build_v1.json'))
 (R/'manifests/step8_freeze_v1.json').write_text(json.dumps(freeze,indent=2)+'\n')
 p=R/'manifests/progress.json';d=json.loads(p.read_text());d['steps'][7].update(status='complete',evidence=['results/step8_complete.md','results/step8_validation.json','manifests/step8_freeze_v1.json'],build_job_id='25832707',native_job_id='25832918');d['next_step']=9;p.write_text(json.dumps(d,indent=2)+'\n')
 print('Step8 frozen:',len(freeze['sha256']),'files')
if __name__=='__main__':main()
