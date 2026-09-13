"""Prepare bounded same-COACH-orbital PT2 gate; never optimize an SCF."""
from pathlib import Path
import json,re,hashlib,shutil
from step4_authority import setrem
R=Path(__file__).resolve().parents[1]
H=Path('/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2/step6_v1')
S=Path('/clusterfs/mhg-data/yaoshen/scf_read/coach_mp2/step6_v1')
I=Path('/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2/step5_import_v1/species')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 cases=[];inp=R/'inputs/step6_v1';inp.mkdir(exist_ok=False);H.mkdir(parents=True,exist_ok=False);(H/'tmp').mkdir()
 for name in ['SIE4x4_h2o','16_C_AE18']:
  for engine,core in [('MP2','FC'),('RIMP2','FC'),('RIMP2','0')]:
   tag=name+'_'+engine+'_'+core;src=I/name;dst=S/tag;dst.mkdir(parents=True,exist_ok=False)
   text=(R/'inputs/step5_native_v2'/(name+'.in')).read_text();text=re.sub(r'(?im)^METHOD\s+.*\n','',text)
   for k,v in dict(EXCHANGE='COACH',CORRELATION=engine,N_FROZEN_CORE=core,N_FROZEN_VIRTUAL=0,SCS=3,SSS_FACTOR=1000000,SOS_FACTOR=1000000,MEM_TOTAL=12000,MEM_STATIC=1500).items():text=setrem(text,k,v)
   p=inp/(tag+'.in');p.write_text(text);hashes={};receipt=json.loads((src/'import.json').read_text())
   for f in ['53.0','54.0','58.0','819.0','99.0','molecule','pseudodata']:
    if (src/f).is_file():
     hashes[f]=sha(src/f);assert hashes[f]==receipt['sha256'][f];shutil.copyfile(src/f,dst/f);assert sha(dst/f)==hashes[f]
   cases.append(dict(tag=tag,species=name,engine=engine,core=core,input=str(p.resolve()),input_sha256=sha(p),scratch=str(dst),source=str(src),source_hashes=hashes))
 protocol=dict(scope='Closed-shell UKS water and triplet UKS carbon, conventional/RI frozen-core and all-electron RI control; not bulk production',solver_dependency=False,omega=.27,ri_conventional_tolerance_hartree=.015/627.50947406,spin_sum_tolerance_hartree=2e-8,parent_energy_tolerance_hartree=2e-8,orbital_invariance='Entire 53.0 byte identity including orbital energies',denominators='Unregularized epsilon_i+epsilon_j-epsilon_a-epsilon_b from unchanged source 53.0; finite strictly negative denominators required',frozen_core='FC must resolve to one occupied orbital per spin for O/C; zero frozen virtuals; explicit all-electron RI control',singles='Record non-Brillouin singles separately, exclude from OS+SS fitted feature',source_definition='EXCHANGE COACH with CORRELATION MP2 or RIMP2, unit spin factors; verify COACH parent energy against Step5',cases=cases)
 (R/'manifests/step6_protocol_v1.json').write_text(json.dumps(protocol,indent=2)+'\n')
 print('Prepared',len(cases),'isolated native evaluations')
if __name__=='__main__':main()
