from pathlib import Path
import struct,json,hashlib
import numpy as np
R=Path(__file__).resolve().parents[1]
def main():
 result=[]
 for name in ['He3_47','He3_48','He3_49']:
  out=Path('/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2/step5_he3_v1')/(name+'.out')
  if not out.exists() or 'Thank you very much for using Q-Chem' not in out.read_text():continue
  src=Path('/global/scratch/users/jsliang/COACH3')/name;dst=Path('/clusterfs/mhg-data/yaoshen/scf_read/coach_mp2/step5_he3_v1')/name;n,m,*_=struct.unpack('<4i',(src/'819.0').read_bytes());a=np.fromfile(src/'53.0',dtype='<f8');b=np.fromfile(dst/'53.0',dtype='<f8');c=a[:2*n*m].reshape(2,m,n);d=b[:2*n*m].reshape(2,m,n);spins=[]
  for s in range(2):
   same=np.max(np.abs(c[s]-d[s]),axis=1);flip=np.max(np.abs(c[s]+d[s]),axis=1);spins.append(dict(exact_columns=int(sum(same==0)),changed_columns=int(sum(same!=0)),max_error_after_sign_alignment=float(np.max(np.minimum(same,flip))),occupied_max_error_after_sign_alignment=float(np.max(np.minimum(same,flip)[:3]))))
  result.append(dict(species=name,spins=spins,orbital_energies_byte_identical=a[2*n*m:2*m*(n+1)].tobytes()==b[2*n*m:2*m*(n+1)].tobytes(),trailing_bytes_identical=a[2*m*(n+1):].tobytes()==b[2*m*(n+1):].tobytes(),source_sha256=hashlib.sha256((src/'53.0').read_bytes()).hexdigest(),output_sha256=hashlib.sha256((dst/'53.0').read_bytes()).hexdigest()))
 files=[Path('/clusterfs/mhg/yaoshen/qchem/trunk')/f for f in ['scfman/scfman.C','libsym/oriorb.F','gesman/GuessMan.C']]
 report=dict(completed_cases=result,source_evidence={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},interpretation='Post-SCF orimo call in scfman.C invokes degenerate orbital orientation and coefficient writeback in oriorb.F. Consistent with observed energy-preserving coefficient changes; strict frozen-MO gate remains failed.',contract_relaxed=False)
 (R/'results/step5_he3_orientation.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
