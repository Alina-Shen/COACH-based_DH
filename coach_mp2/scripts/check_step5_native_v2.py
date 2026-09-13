from pathlib import Path
import json,hashlib,struct,argparse
import numpy as np
from active_input_authority import load_rows
from validate_step2_fixed import parse
R=Path(__file__).resolve().parents[1];H=Path('/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2/step5_native_v2')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def close_with_dispersion(energy):
 if energy.get('dispersion_in_component_sum'):raise ValueError('dispersion already included')
 energy=dict(energy)
 energy['nondispersion_component_sum_hartree']=energy['component_sum_hartree']
 energy['component_sum_hartree']+=energy['dispersion_hartree']
 energy['closure_error_hartree']=energy['component_sum_hartree']-energy['energy_hartree']
 energy['dispersion_in_component_sum']=True
 return energy
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--partial',action='store_true');args=parser.parse_args();cases=json.loads((R/'manifests/step5_native_v2.json').read_text())['cases'];rows={r['species']:r for r in load_rows()};results=[]
 build=json.loads((R/'manifests/step5_no_orientation_build_v1.json').read_text());assert sha(Path(build['binary']))==build['binary_sha256']
 baseline=json.loads((R/'results/step2_fixed_v3_validation.json').read_text());references={r['species']:r['energy_hartree'] for r in baseline['cases']}
 references.update({r['species']:r['energy']['energy_hartree'] for r in json.loads((R/'results/step5_he3_native_validation.json').read_text())['cases']})
 for case in cases:
  assert sha(Path(case['input']))==case['input_sha256']
  name=case['species'];out=H/(name+'.out')
  if args.partial and (not out.exists() or 'Thank you very much for using Q-Chem' not in out.read_text()):continue
  text=out.read_text();energy=close_with_dispersion(parse(text));assert 'COACH_MP2: preserving saved MOs; skipping post-SCF orientation' in text
  src=Path(case['source']);dst=Path(case['scratch']);n,m,*_=struct.unpack('<4i',(src/'819.0').read_bytes());assert n==int(rows[name]['orbital_spherical_aos'])
  v=np.fromfile(src/'53.0',dtype='<f8');coeff=v[:2*n*m].reshape(2,m,n);ne=int(rows[name]['electron_count']);spin=int(rows[name]['multiplicity'])-1;occ=[(ne+spin)//2,(ne-spin)//2];checks=[]
  for path in [src/'54.0',dst/'54.0']:
   density=np.fromfile(path,dtype='<f8').reshape(2,n,n)
   for s,k in enumerate(occ):
    reconstructed=coeff[s,:k].T@coeff[s,:k];error=float(np.max(np.abs(reconstructed-density[s])));bound=float(16*np.finfo(float).eps*np.sum(coeff[s,:k]**2));checks.append(dict(path=str(path),spin=s,error=error,bound=bound,passed=bool(np.isfinite(density).all() and error<=bound)))
  overlap=np.fromfile(dst/'320.0',dtype='<f8').reshape(n,n)
  gram_errors=[float(np.max(np.abs(c@overlap@c.T-np.eye(m)))) for c in coeff]
  overlap_ok=bool(np.isfinite(overlap).all() and max(gram_errors)<=1e-6)
  same=sha(dst/'53.0')==case['source_hashes']['53.0'];source_ok=all(sha(src/f)==h for f,h in case['source_hashes'].items());diff=energy['energy_hartree']-references[name] if name in references else None
  passed=bool(overlap_ok and same and source_ok and np.isfinite(v).all() and all(c['passed'] for c in checks) and abs(energy['closure_error_hartree'])<=2e-8 and (diff is None or abs(diff)<=2e-8))
  results.append(dict(species=name,passed=passed,mo_file_byte_unchanged=same,source_MO_orthonormality_errors=gram_errors,orthonormality_tolerance=1e-6,overlap_sha256=sha(dst/'320.0'),source_unchanged=source_ok,density_checks=checks,energy=energy,prior_parent_energy_difference=diff,output_sha256=sha(out)))
 report=dict(job_id='25827314',completed=len(results),passed=len(results)==6 and all(r['passed'] for r in results),cases=results,scope='Six fixed-parent read regressions; not MP2 validation or proof of historical basis identity')
 (R/'results/step5_native_v2_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
 if not args.partial:assert report['passed']
if __name__=='__main__':main()
