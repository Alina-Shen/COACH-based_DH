"""Five-source numerical diagnostic, not a full-domain numerical release gate."""
from pathlib import Path
import numpy as np,struct,json,csv,hashlib
ROOT=Path(__file__).resolve().parents[1]
def main():
 rows={r['species']:r for r in csv.DictReader((ROOT/'manifests/step4_inputs_v1.csv').open())};reports=[]
 for name in ['16_C_AE18','SIE4x4_h2o','AE11_Yb','O24x5_he2_1.0','L14_2a']:
  r=rows[name];p=Path('/global/scratch/users/jsliang/BigNC/COACH' if name=='L14_2a' else '/global/scratch/users/jsliang/COACH3')/name
  n,m,*_=struct.unpack('<4i',(p/'819.0').read_bytes());v=np.fromfile(p/'53.0',dtype='<f8');d=np.fromfile(p/'54.0',dtype='<f8').reshape(2,n,n)
  coeff=v[:2*n*m].reshape(2,m,n);ne=int(r['electron_count']);spin=int(r['multiplicity'])-1;occs=[(ne+spin)//2,(ne-spin)//2];errors=[]
  for s,k in enumerate(occs):
   reconstructed=coeff[s,:k].T@coeff[s,:k];bound=16*np.finfo(float).eps*max(np.sum(coeff[s,:k]**2),np.finfo(float).tiny)
   errors.append(dict(max_error=float(np.max(np.abs(reconstructed-d[s]))),normwise_bound=float(bound),passed=bool(np.max(np.abs(reconstructed-d[s]))<=bound)))
  reports.append(dict(species=name,nao=n,nmo=m,authority_nao=int(r['orbital_spherical_aos']),finite=bool(np.isfinite(v).all() and np.isfinite(d).all()),density=errors,source_hashes={str(p/f):hashlib.sha256((p/f).read_bytes()).hexdigest() for f in ['819.0','53.0','54.0']}))
 (ROOT/'results/step5_sample_numerics.json').write_text(json.dumps(reports,indent=2)+'\n')
 assert all(r['finite'] and r['nao']==r['authority_nao'] and all(d['passed'] for d in r['density']) for r in reports)
 print('Five numerical samples PASS')
if __name__=='__main__':main()
