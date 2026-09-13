from pathlib import Path
import json,hashlib,struct,argparse
import numpy as np
from validate_step2_fixed import parse
R=Path(__file__).resolve().parents[1];H=Path('/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2/step5_he3_v1')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--partial',action='store_true');args=parser.parse_args()
 manifest=json.loads((R/'manifests/step5_he3_v1.json').read_text());results=[]
 for case in manifest['cases']:
  name=case['species'];src=Path(case['source']);scratch=Path(case['scratch']);out=H/(name+'.out')
  if args.partial and (not out.exists() or 'Thank you very much for using Q-Chem' not in out.read_text()):continue
  energy=parse(out.read_text());n,m,*_=struct.unpack('<4i',(src/'819.0').read_bytes());v=np.fromfile(src/'53.0',dtype='<f8');c=v[:2*n*m].reshape(2,m,n);eps=v[2*n*m:2*m*(n+1)].reshape(2,m)
  source_unchanged=all(sha(src/f)==h for f,h in case['source_hashes'].items());mo_unchanged=sha(scratch/'53.0')==case['source_hashes']['53.0'];bounds=[]
  for densityfile in [src/'54.0',scratch/'54.0']:
   d=np.fromfile(densityfile,dtype='<f8').reshape(2,n,n)
   for s in range(2):
    reconstructed=c[s,:3].T@c[s,:3];bound=16*np.finfo(float).eps*np.sum(c[s,:3]**2);error=float(np.max(np.abs(reconstructed-d[s])));bounds.append(dict(path=str(densityfile),spin=s,error=error,bound=float(bound),passed=bool(np.isfinite(d).all() and error<=bound)))
  valid=bool(np.isfinite(v).all() and np.isfinite(eps).all() and source_unchanged and mo_unchanged and all(b['passed'] for b in bounds) and abs(energy['closure_error_hartree'])<=2e-8)
  results.append(dict(species=name,passed=valid,source_unchanged=source_unchanged,mo_file_byte_unchanged=mo_unchanged,energy=energy,density_checks=bounds,active_orbital_energies_finite=bool(np.isfinite(eps).all()),output_sha256=sha(out),trailing_bytes_preserved=(len(v)-2*m*(n+1))*8))
 report=dict(job_id='25826223',passed=len(results)==3 and all(r['passed'] for r in results),completed_cases=len(results),completed_cases_passed=bool(results) and all(r['passed'] for r in results),cases=results,scope='native fixed-parent read and unchanged legacy MO/energy bytes; not MP2 or virtual-space completeness validation')
 (R/'results/step5_he3_native_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));assert report['completed_cases_passed'] if args.partial else report['passed']
if __name__=='__main__':main()
