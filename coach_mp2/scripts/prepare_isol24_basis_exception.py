from pathlib import Path
import json,hashlib,tarfile,csv,os,struct
R=Path(__file__).resolve().parents[1]
os.environ['TMPDIR']=str(R/'runtime')
from pyscf import gto
from step4_authority import setrem
from audit_step4_inputs import parse
from inventory_step5 import atoms
from collections import Counter

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 pointer=json.loads((R/'manifests/step4_snapshot_v1.json').read_text());name='ISOL24_i8e'
 with tarfile.open(Path(pointer['snapshot'])/'inputs.tar') as t:old=t.extractfile('coach/'+name+'.in').read().decode()
 new=setrem(old,'BASIS','def2-QZVPP');a,ar,*_=parse(old);b,br,*_=parse(new)
 assert {k:v for k,v in a.items() if k!='rem'}=={k:v for k,v in b.items() if k!='rem'}
 assert {k for k in ar if ar[k]!=br[k]}=={'BASIS'}
 out=R/'inputs/basis_exceptions_v1'/f'{name}.in';out.parent.mkdir(exist_ok=True);out.write_text(new)
 counts=Counter(x[0] for x in atoms(new)[2]);bases={e:gto.basis.load('def2-qzvpp',e) for e in counts}
 shells=sum(counts[e]*sum(len(s[1])-1 for s in bases[e]) for e in counts)
 nao=sum(counts[e]*sum((2*s[0]+1)*(len(s[1])-1) for s in bases[e]) for e in counts)
 source=Path('/global/scratch/users/jsliang/COACH3')/name;dims=struct.unpack('<4i',(source/'819.0').read_bytes());assert nao==dims[0]==1884
 override=dict(species=name,orbital_basis='def2-QZVPP',orbital_spherical_aos=str(nao),orbital_shells=str(shells),derived_sha256=sha(out))
 d=dict(schema_version=1,date='2026-09-12',authority='explicit user instruction',precedence='This species-specific amendment supersedes the Step4 v1 orbital basis for ISOL24_i8e only; previous frozen evidence is historical.',base_manifest='manifests/step4_inputs_v1.csv',base_manifest_sha256=sha(R/'manifests/step4_inputs_v1.csv'),overrides={name:override},input_overrides={name:dict(path=str(out.relative_to(R)),sha256=sha(out))},old_orbital_basis='def2-QZVPPD',auxiliary_basis=br['AUX_BASIS_CORR'],auxiliary_policy='Existing RIMP2-def2-QZVPPD auxiliary assignment retained; user changed orbital basis only.',source_dimensions=list(dims),source_dimensions_sha256=sha(source/'819.0'),basis_identity='AO count agrees; full generating-basis identity and native compatibility remain unproven',comparison_caveat='Intentional single-species departure from revwb97m2/XYG-OS5/wb97m_os_rimp2 orbital basis; report in reproducibility and benchmark limitations',new_scf_authorized=False)
 (R/'configs/input_basis_amendments_v1.json').write_text(json.dumps(d,indent=2)+'\n')
 print('Only BASIS changed; AO count',nao,'shells',shells,'auxiliary retained',br['AUX_BASIS_CORR'])
if __name__=='__main__':main()
