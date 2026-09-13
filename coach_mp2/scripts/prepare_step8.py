from pathlib import Path
import json,hashlib,shutil,re
from step4_authority import setrem
R=Path(__file__).resolve().parents[1];H=Path('/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2/step8_v1');S=Path('/clusterfs/mhg-data/yaoshen/scf_read/coach_mp2/step8_v1');I=Path('/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2/step5_import_v1/species')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 H.mkdir(parents=True,exist_ok=False);(H/'tmp').mkdir();inp=R/'inputs/step8_v1';inp.mkdir();cases=[]
 for name in ['SIE4x4_h2o','16_C_AE18']:
  base=(R/'inputs/step5_native_v2'/(name+'.in')).read_text();src=I/name;receipt=json.loads((src/'import.json').read_text())
  for mode in ['250974','99590','75302','sr_vv','full_hf','lr_hf']:
   tag=name+'_'+mode;text=base
   if mode.isdigit():
    text=setrem(text,'XC_GRID',{'250974':'000250000974','99590':'000099000590','75302':'000075000302'}[mode]);text=setrem(text,'XC_FXC',3)
   else:
    text=re.sub(r'(?im)^(METHOD|AUX_BASIS_CORR)\s+.*\n','',text);text=setrem(text,'EXCHANGE','HF')
    if mode!='full_hf':
     for k,v in dict(LRC_DFT='TRUE',SRC_DFT='TRUE',OMEGA=270,OMEGA2=270,HF_SR=1000 if mode=='sr_vv' else 0,HF_LR=0 if mode=='sr_vv' else 1000).items():text=setrem(text,k,v)
    if mode=='sr_vv':
     for k,v in dict(NL_CORRELATION='VV10',NL_GRID=1,NL_VV_B=550,NL_VV_C=100,NL_VV_SCALE=100000).items():text=setrem(text,k,v)
   p=inp/(tag+'.in');p.write_text(text);dst=S/tag;dst.mkdir(parents=True,exist_ok=False);hashes={}
   for f in ['53.0','54.0','58.0','819.0','99.0','molecule','pseudodata']:
    if (src/f).is_file():hashes[f]=sha(src/f);assert hashes[f]==receipt['sha256'][f];shutil.copyfile(src/f,dst/f);assert sha(dst/f)==hashes[f]
   cases.append(dict(tag=tag,species=name,mode=mode,input=str(p.resolve()),input_sha256=sha(p),scratch=str(dst),source=str(src),source_hashes=hashes))
 cols=[f'{channel}_v{i}_u{j}' for channel in ['X','CSS','COS'] for i in range(12) for j in range(8)]+['SRHF','VV10','PT2_OS_plus_SS','D4_ATM']
 report=dict(scope='Two-species native three-grid/scalar gateway; D4 nonzero geometry-only check uses existing ISOL24 output',omega=.27,gamma_ss=.01,grids=['250974','99590','75302'],rows=[64,154,166],columns=cols,full_matrix_rtol=2e-12,full_matrix_atol=2e-12,energy_identity_tolerance_hartree=1e-8,cross_engine_parent_tolerance_hartree=2e-6,pt2_reuse='Step6 approved-basis FC results, with user-deferred carbon RI error',solver_dependency=False,cases=cases)
 (R/'manifests/step8_protocol_v1.json').write_text(json.dumps(report,indent=2)+'\n')
 # Isolated Python reference copies; adapt the frozen omega only.
 pkg=R/'scripts/step8_reference';pkg.mkdir(exist_ok=False);(pkg/'__init__.py').write_text('');pins={}
 for f in ['integrated_dv.py','qchem_integrated_dv_reference.py']:
  src=R.parent/'revwb97m2'/f;pins[str(src)]=sha(src);text=src.read_text()
  if f=='integrated_dv.py':assert text.count('omega: float = 0.3')==1;text=text.replace('omega: float = 0.3','omega: float = 0.27')
  (pkg/f).write_text(text)
 (R/'manifests/step8_reference_provenance_v1.json').write_text(json.dumps(dict(source_sha256=pins,adaptation='omega=.27; no changes to mathematical formulas or row semantics'),indent=2)+'\n');print('Prepared',len(cases),'native cases')
if __name__=='__main__':main()
