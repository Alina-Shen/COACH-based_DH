from pathlib import Path
import json,hashlib,shutil
from step4_authority import setrem
R=Path(__file__).resolve().parents[1];S=Path('/clusterfs/mhg-data/yaoshen/scf_read/coach_mp2/step5_he3_v1');H=Path('/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2/step5_he3_v1')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 cases=[];(R/'inputs/step5_he3_v1').mkdir(exist_ok=True)
 for name in ['He3_47','He3_48','He3_49']:
  p=Path('/clusterfs/mhg-data/yaoshen/GSCDB/qchem_inputs')/(name+'.in');text=p.read_text()
  for k,v in dict(METHOD='COACH',SCF_GUESS='READ',GEN_SCFMAN='FALSE',MAX_SCF_CYCLES='0',MP2_RESTART_NO_SCF='TRUE',NO_ORTHO='TRUE',SCF_FINAL_PRINT='1').items():text=setrem(text,k,v)
  inp=R/'inputs/step5_he3_v1'/(name+'.in');inp.write_text(text);dest=S/name;dest.mkdir(parents=True,exist_ok=False);hashes={}
  for fn in ['53.0','54.0','58.0','819.0','99.0','molecule','pseudodata']:
   src=Path('/global/scratch/users/jsliang/COACH3')/name/fn
   if src.is_file():
    shutil.copyfile(src,dest/fn);hashes[fn]=sha(src);assert sha(dest/fn)==hashes[fn]
  cases.append(dict(species=name,input=str(inp),input_sha256=sha(inp),source=str(src.parent),scratch=str(dest),source_hashes=hashes))
 H.mkdir(parents=True,exist_ok=False);(H/'tmp').mkdir()
 (R/'manifests/step5_he3_v1.json').write_text(json.dumps(dict(cases=cases,no_orbital_update=True),indent=2)+'\n')
if __name__=='__main__':main()
