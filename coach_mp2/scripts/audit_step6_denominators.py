from pathlib import Path
import json,struct,hashlib
import numpy as np
from step6_numerics import spectrum,denominator_ranges
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 cases=json.loads((R/'manifests/step6_protocol_v1.json').read_text())['cases']+json.loads((R/'manifests/step6_conventional_v2.json').read_text())['cases'];results=[]
 for c in cases:
  src=Path(c['source']);dst=Path(c['scratch']);n,m,*_=struct.unpack('<4i',(src/'819.0').read_bytes());v=np.fromfile(src/'53.0',dtype='<f8');coef=v[:2*n*m].reshape(2,m,n);saved=v[2*n*m:2*m*(n+1)].reshape(2,m);occ=[5,5] if c['species']=='SIE4x4_h2o' else [4,2]
  f=np.fromfile(dst/'58.0',dtype='<f8').reshape(2,n,n);refroot=Path('/clusterfs/mhg-data/yaoshen/scf_read/coach_mp2/step5_native_v2')/c['species'];ref=np.fromfile(refroot/'58.0',dtype='<f8').reshape(2,n,n)
  e=[];er=[];ov=[];density=[]
  for s in range(2):
   a,b=spectrum(coef[s],f[s],occ[s]);e.append(a);ov.append(b);er.append(spectrum(coef[s],ref[s],occ[s])[0]);d=coef[s,:occ[s]].T@coef[s,:occ[s]];actual=np.fromfile(dst/'54.0',dtype='<f8').reshape(2,n,n)[s];err=float(abs(d-actual).max());bound=float(16*np.finfo(float).eps*np.sum(coef[s,:occ[s]]**2));density.append(dict(error=err,bound=bound,passed=err<=bound))
  diff=float(np.max(np.abs(np.array(e)-er)));same=sha(dst/'53.0')==c['source_hashes']['53.0'];source_ok=all(sha(src/k)==h for k,h in c['source_hashes'].items())
  results.append(dict(tag=c['tag'],nAO=n,nMO=m,occupations=occ,core_per_spin=1 if c['core']=='FC' else 0,virtuals=[m-o for o in occ],source_unchanged=source_ok,MO_file_unchanged=same,Fock_vs_COACH_baseline_max_error=float(abs(f-ref).max()),native_spectrum_vs_COACH_baseline_max_error=diff,saved_eigenvalues_vs_native_spectrum_max_difference=float(np.max(np.abs(np.array(e)-saved))),occupied_virtual_Fock_max=ov,denominators=denominator_ranges(e,occ,1 if c['core']=='FC' else 0),density=density,passed=bool(diff<=2e-8 and same and source_ok and all(x['passed'] for x in density)),fock_sha256=sha(dst/'58.0'),baseline_fock_sha256=sha(refroot/'58.0')))
 report=dict(passed=all(c['passed'] for c in results),cases=results,definition='Native COACH Fock projected into unchanged source occupied/virtual spaces; eigenvalues of each block. Not blindly archived 53.0 energies. No occupied-virtual rotation, attenuation or regularization.');(R/'results/step6_denominator_audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));assert report['passed']
if __name__=='__main__':main()
