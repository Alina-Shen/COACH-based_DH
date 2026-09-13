from pathlib import Path
import json,tarfile,shutil,hashlib
from step4_authority import setrem
R=Path(__file__).resolve().parents[1];S=Path('/clusterfs/mhg-data/yaoshen/scf_read/coach_mp2/step5_native_v2');H=Path('/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2/step5_native_v2')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 cfg=json.loads((R/'configs/input_basis_amendments_v1.json').read_text());pointer=json.loads((R/'manifests/step4_snapshot_v1.json').read_text());cases=[];inp=R/'inputs/step5_native_v2';inp.mkdir(exist_ok=False)
 with tarfile.open(Path(pointer['snapshot'])/'inputs.tar') as tar:
  for name in ['SIE4x4_h2o','16_C_AE18','He3_47','He3_48','He3_49','ISOL24_i8e']:
   text=(R/cfg['input_overrides'][name]['path']).read_text() if name in cfg['input_overrides'] else tar.extractfile('coach/'+name+'.in').read().decode()
   for k,v in dict(METHOD='COACH',SCF_GUESS='READ',SCF_GUESS_MIX='0',GEN_SCFMAN='FALSE',MAX_SCF_CYCLES='0',MP2_RESTART_NO_SCF='TRUE',NO_ORTHO='TRUE',SCF_FINAL_PRINT='1').items():text=setrem(text,k,v)
   f=inp/(name+'.in');f.write_text(text);dest=S/name;dest.mkdir(parents=True,exist_ok=False);src=Path('/global/scratch/users/jsliang/COACH3')/name;hashes={}
   for filename in ['53.0','54.0','58.0','819.0','99.0','molecule','pseudodata']:
    p=src/filename
    if p.is_file():shutil.copyfile(p,dest/filename);hashes[filename]=sha(p);assert sha(dest/filename)==hashes[filename]
   cases.append(dict(species=name,input=str(f),input_sha256=sha(f),scratch=str(dest),source=str(src),source_hashes=hashes))
 H.mkdir(parents=True,exist_ok=False);(H/'tmp').mkdir()
 (R/'manifests/step5_native_v2.json').write_text(json.dumps(dict(cases=cases,scope='fixed parent read; patched post-SCF orientation; ISOL24 approved basis; no new SCF'),indent=2)+'\n')
if __name__=='__main__':main()
