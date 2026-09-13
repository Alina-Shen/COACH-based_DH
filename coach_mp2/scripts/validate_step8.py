from pathlib import Path
import json,hashlib,struct,csv,os,re,importlib.util
import numpy as np
from step8_validation_helpers import scalar,parse_matrix,iter_diagnostic
from step8_reference.qchem_integrated_dv_reference import full_integrated_dv_block
from step8_reference.integrated_dv import selected_integrated_dv_block as integrate_block
R=Path(__file__).resolve().parents[1];H=Path('/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2/step8_v1')
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 return h.hexdigest()
def hf(text):return scalar(text,r'Alpha\s+Exchange\s+Energy')+scalar(text,r'Beta\s+Exchange\s+Energy')
def base_energy(t):return sum(scalar(t,k) for k in [r'One-Electron\s+Energy',r'Total\s+Coulomb\s+Energy',r'Nuclear\s+Repu\.\s+Energy'])
def main():
 proto=json.loads((R/'manifests/step8_protocol_v1.json').read_text());build=json.loads((R/'manifests/step8_build_v1.json').read_text());assert sha(build['binary'])==build['binary_sha256'];assert sha(build['libks'])==build['libks_sha256'];assert build['libks'] in (H/'loaded_libraries.txt').read_text()
 for f,h in json.loads((R/'manifests/step6_freeze_v1.json').read_text())['sha256'].items():assert sha(R/f)==h,f
 features={};reports=[];texts={}
 for c in proto['cases']:
  tag=c['tag'];src=Path(c['source']);dst=Path(c['scratch']);out=H/(tag+'.out');t=out.read_text();texts[tag]=t;assert sha(c['input'])==c['input_sha256'];assert 'Thank you very much for using Q-Chem' in t;assert 'The orbitals will not be altered' in t;assert 'COACH_MP2: preserving saved MOs' in t
  assert all(sha(src/f)==h for f,h in c['source_hashes'].items());assert sha(dst/'53.0')==c['source_hashes']['53.0']
  n,m,*_=struct.unpack('<4i',(src/'819.0').read_bytes());coef=np.fromfile(src/'53.0',dtype='<f8')[:2*n*m].reshape(2,m,n);occ=[5,5] if c['species']=='SIE4x4_h2o' else [4,2];den=np.fromfile(dst/'54.0',dtype='<f8').reshape(2,n,n)
  for s,o in enumerate(occ):assert np.max(abs(coef[s,:o].T@coef[s,:o]-den[s]))<=16*np.finfo(float).eps*np.sum(coef[s,:o]**2)
  row=dict(tag=tag,source_MO_unchanged=True,density_pass=True,output_sha256=sha(out))
  if c['mode'].isdigit():
   native,count=parse_matrix(t);ref=np.zeros((96,180));selected=np.zeros((3,96));points=0
   for a in iter_diagnostic(H/(tag+'.bin')):
    args=(a[:,0],a[:,1],a[:,2],a[:,3:6],a[:,6:9],a[:,9],a[:,10]);ref+=full_integrated_dv_block(*args);selected+=integrate_block(*args);points+=len(a)
   error=float(abs(native-ref).max());err2=float(abs(native.T[[64,154,166]]-selected).max());assert np.allclose(native,ref,rtol=proto['full_matrix_rtol'],atol=proto['full_matrix_atol']);assert np.allclose(native.T[[64,154,166]],selected,rtol=2e-12,atol=2e-12)
   features[tag]=native.T[[64,154,166]].reshape(288);row.update(full_matrix_max_error=error,independent_selected_max_error=err2,points=points,complete_blocks=count,density_dump_sha256=sha(H/(tag+'.bin')))
   np.save(H/(tag+'_full.npy'),native.T);np.save(H/(tag+'_selected.npy'),features[tag]);print(tag,'reference PASS',error,flush=True)
  row['passed']=True;reports.append(row)
 # Use pinned reference geometry-only implementation; does not import/run parent SCF.
 refpath=R.parent/'revwb97m2/qchem_scalar_features.py';spec=importlib.util.spec_from_file_location('readonly_scalar',refpath);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 scalars={};tol=proto['energy_identity_tolerance_hartree'];pt2={c['species']:c for c in json.loads((R/'results/step6_validation.json').read_text())['cases'] if c['core']=='FC' and c['pt2']['engine']=='RIMP2'}
 for name in ['SIE4x4_h2o','16_C_AE18']:
  sr=texts[name+'_sr_vv'];full=texts[name+'_full_hf'];lr=texts[name+'_lr_hf'];ehfsr=hf(sr);ehflr=hf(lr);ehffull=hf(full);vv=scalar(sr,r'DFT\s+Correlation\s+Energy');fixed=base_energy(full)+ehflr;assert abs(ehfsr+ehflr-ehffull)<=tol
  assert abs(base_energy(full)+ehffull-scalar(full,r'SCF\s+energy'))<=tol
  assert abs(base_energy(sr)+ehfsr+vv-scalar(sr,r'SCF\s+energy'))<=tol
  assert abs(base_energy(lr)+ehflr-scalar(lr,r'SCF\s+energy'))<=tol
  parent_errors={}
  for grid in proto['grids']:
   t=texts[name+'_'+grid];slx=scalar(t,r'DFT\s+Exchange\s+Energy');slc_plus_vv=scalar(t,r'DFT\s+Correlation\s+Energy');total=fixed+.22878981*ehfsr+slx+slc_plus_vv;observed=scalar(t,r'SCF\s+energy');parent_errors[grid]=total-observed;assert abs(total-observed)<=tol
  atm=mod.evaluate_d4_atm_from_qchem_input((R/'inputs/step5_native_v2'/(name+'.in')).read_text());p=pt2[name]['pt2'];scalars[name]=dict(SRHF=ehfsr,LRHF=ehflr,full_HF=ehffull,VV10=vv,PT2_OS=p['opposite_spin'],PT2_SS=p['same_spin'],PT2_total=p['doubles'],D4_ATM=atm,E_fixed=fixed,hf_split_error=ehfsr+ehflr-ehffull,parent_reconstruction_errors=parent_errors,carbon_RI_accuracy_deferred=name=='16_C_AE18')
 # Nonzero ATM check against an already validated native COACH calculation.
 inp=R/'inputs/step5_native_v2/ISOL24_i8e.in';out=Path('/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2/step5_native_v2/ISOL24_i8e.out');atm=mod.evaluate_d4_atm_from_qchem_input(inp.read_text());native_atm=scalar(out.read_text(),r'-D4 energy including 3-body term');assert abs(atm-native_atm)<=tol;assert abs(native_atm)>1e-6
 # Atomic publication only after every gate. No fitting coefficients or solver used.
 stage=H/'features.staging';dest=H/'features';assert not stage.exists() and not dest.exists();stage.mkdir();arrays={}
 for name,s in scalars.items():
  for grid in proto['grids']:
   vector=np.r_[features[name+'_'+grid],[s['SRHF'],s['VV10'],s['PT2_total'],s['D4_ATM']]];assert vector.shape==(292,) and np.isfinite(vector).all();p=stage/(name+'_'+grid+'.npy');np.save(p,vector);arrays[p.name]=sha(p)
  for grid in ['99590','75302']:
   diff=np.r_[features[name+'_'+grid]-features[name+'_250974'],np.zeros(4)];p=stage/(name+'_delta_'+grid+'.npy');np.save(p,diff);arrays[p.name]=sha(p)
 metadata=dict(columns=proto['columns'],rows=proto['rows'],omega=.27,gamma_ss=.01,grid_difference_sign='coarser minus 250974',scalar_grid_differences='zero: HF/PT2/ATM are grid-independent; VV10 evaluated once on fixed SG-1',scalars=scalars,sha256=arrays,scope='pilot only; carbon RI accuracy explicitly deferred by user',protocol_sha256=sha(R/'manifests/step8_protocol_v1.json'))
 (stage/'manifest.json').write_text(json.dumps(metadata,indent=2)+'\n')
 for p in stage.iterdir():p.chmod(0o444)
 stage.rename(dest)
 report=dict(step=8,passed=True,cases=reports,scalars=scalars,d4_nonzero_check=dict(species='ISOL24_i8e',external=atm,native=native_atm,difference=atm-native_atm,input_sha256=sha(inp),output_sha256=sha(out)),d4_helper_sha256=sha(refpath),feature_manifest_sha256=sha(dest/'manifest.json'),output=str(dest),solver_used=False,scope='two-species native three-grid/scalar feature gateway; not production')
 (R/'results/step8_validation.json').write_text(json.dumps(report,indent=2)+'\n');print('STEP8 PASS',flush=True)
if __name__=='__main__':main()
