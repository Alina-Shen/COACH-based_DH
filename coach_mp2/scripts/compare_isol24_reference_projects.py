"""Read-only evidence for ISOL24_i8e handling in three reference projects."""
from pathlib import Path
import hashlib,json,re,struct
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 data={'species':'ISOL24_i8e','date':'2026-09-12','benchmarks':{},'archives':{}}
 for name in ['wb97m_os_rimp2','xyg_os5']:
  root=Path('/clusterfs/mhg-data/yaoshen/wb97m_os/GSCDB')/name/'work';files=[root/('ISOL24_i8e'+ext) for ext in ['.in','.out','.sh']];out=files[1].read_text();selected=[]
  for i,line in enumerate(out.splitlines(),1):
   if re.search('basis functions|Convergence criterion met|Exchange:|Correlation:|Coulomb attenuation|Inconsistent size|Size of previous|Thank you',line):selected.append({'line':i,'text':line})
  data['benchmarks'][name]={'sources':{str(p):sha(p) for p in files},'output_evidence':selected,'rem':files[0].read_text().split('$rem',1)[1].split('$end',1)[0]}
 for root in ['/global/scratch/users/jsliang/COACH3','/global/scratch/users/jsliang/wB97M-V','/clusterfs/mhg-data/yaoshen/scf_read/wb97m_os_rimp2','/clusterfs/mhg-data/yaoshen/scf_read/xyg_os5']:
  p=Path(root)/'ISOL24_i8e';dim=p/'819.0';data['archives'][str(p)]={'dimensions':struct.unpack('<4i',dim.read_bytes()),'dimensions_sha256':sha(dim),'mo_file_bytes':(p/'53.0').stat().st_size,'qarchive_bytes':(p/'qarchive.h5').stat().st_size}
 policy=R.parent/'revwb97m2/manifests/qchem_orbitals/qchem_orbital_authority_v1.yaml';data['revwb97m2']={'authority_path':str(policy),'authority_sha256':sha(policy),'canonical_source':'/clusterfs/mhg-data/yaoshen/scf_read/wb97m_os_rimp2','scope':'source-selection policy and current source dimensions; not proof of species-specific revwb97m2 feature completion'}
 data['provenance_limit']='Successful outputs show correct-basis SCF, not how the initial read guesses were obtained or how the shared 1884-AO source was superseded. No undocumented projection/repair is inferred.'
 (R/'results/step5_isol24_reference_comparison.json').write_text(json.dumps(data,indent=2)+'\n')
if __name__=='__main__':main()
