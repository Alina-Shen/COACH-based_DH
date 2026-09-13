from pathlib import Path
import json,hashlib,re,difflib,struct,os
os.environ['TMPDIR']=str(Path(__file__).resolve().parents[1]/'runtime')
from pyscf import gto
from inventory_step5 import atoms
from collections import Counter
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 result={'cases':[],'job_id':'25826223'}
 for name in ['ISOL24_i8e','He3_47','He3_48','He3_49']:
  a=Path('/clusterfs/mhg-data/yaoshen/GSCDB/qchem_inputs')/(name+'.in');b=Path('/clusterfs/mhg-data/yaoshen/wb97m_os/GSCDB/xyg_os5/work')/(name+'.in');o=b.with_suffix('.out');source=Path('/global/scratch/users/jsliang/COACH3')/name
  evidence=[l for l in o.read_text(errors='replace').splitlines() if re.search('basis functions|previous SCF|Inconsistent|Thank you',l)]
  result['cases'].append(dict(species=name,source_hashes={str(p):sha(p) for p in [a,b,o,source/'819.0']},geometry_equal=atoms(a.read_text())==atoms(b.read_text()),input_diff=''.join(difflib.unified_diff(a.read_text().splitlines(True),b.read_text().splitlines(True),fromfile='GSCDB',tofile='XYGOS5')),xyg_output_evidence=evidence,legacy_dimensions=struct.unpack('<4i',(source/'819.0').read_bytes())))
 counts=Counter(x[0] for x in atoms(Path('/clusterfs/mhg-data/yaoshen/GSCDB/qchem_inputs/ISOL24_i8e.in').read_text())[2]);result['ISOL24_element_counts']=dict(counts);result['ISOL24_candidate_basis_counts']={}
 for label in ['def2-qzvppd','def2-qzvpp','def2-qzvp','def2-tzvppd','def2-tzvpp']:
  per={e:sum((2*s[0]+1)*(len(s[1])-1) for s in gto.basis.load(label,e)) for e in counts}
  result['ISOL24_candidate_basis_counts'][label]=dict(per_element=per,total=sum(counts[e]*per[e] for e in counts))
 result['ISOL24_inference']='1884 matches non-diffuse def2-QZVPP/QZVP counts; generating basis not proven by count alone.'
 (R/'results/step5_quarantine_investigation.json').write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':main()
