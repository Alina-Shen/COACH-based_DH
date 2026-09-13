from pathlib import Path
import hashlib,json,re,shutil,argparse
ROOT=Path(__file__).resolve().parents[1]
SCRATCH=Path('/clusterfs/mhg-data/yaoshen/scf_read/coach_mp2/step2_fixed_v3')
HEAVY=Path('/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2/step2_fixed_v3')
def record(p):return dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--stage',action='store_true');a=parser.parse_args()
 manifest={'cases':[],'scope':'two species; no-diagonalization fixed COACH energy evaluation','reference':'COACH fixtures plus paper workbook AE18_6 carbon reference','tolerance_hartree':2e-6}
 for species in ['SIE4x4_h2o','16_C_AE18']:
  source=Path('/clusterfs/mhg-data/yaoshen/GSCDB/qchem_inputs')/(species+'.in')
  text=source.read_text();text,n=re.subn(r'(?im)^method\s+\S+', 'METHOD COACH',text);assert n==1
  for mode in ['fixed']:
   content=text
   if mode=='fixed':content,n=re.subn(r'(?im)^max_scf_cycles\s+\d+', 'MAX_SCF_CYCLES 0',content);assert n==1
   content=content.replace('GEN_SCFMAN TRUE','GEN_SCFMAN FALSE').replace('$rem','$rem\nNO_ORTHO TRUE\nMP2_RESTART_NO_SCF TRUE\nSCF_GUESS READ\nSCF_FINAL_PRINT 1',1)
   inp=ROOT/'inputs/step2_fixed_v3'/f'{species}_{mode}.in';inp.write_text(content)
   dest=SCRATCH/f'{species}_{mode}'
   files=[]
   for name in ['53.0','54.0','58.0','819.0','99.0','molecule','pseudodata']:
    p=Path('/global/scratch/users/jsliang/COACH3')/species/name
    if p.is_file():
     files.append(record(p))
     if a.stage:
      dest.mkdir(parents=True,exist_ok=True);target=dest/name
      if target.exists():raise ValueError('Refuse overwrite '+str(target))
      shutil.copyfile(p,target);assert record(target)['sha256']==files[-1]['sha256']
   manifest['cases'].append(dict(species=species,mode=mode,input=record(inp),source_input=record(source),scratch=str(dest),source_files=files))
 qc=Path('/clusterfs/mhg/yaoshen/qchem/trunk')
 manifest['runtime']=[record(qc/p) for p in ['bin/qchem','build/qcprog.exe','libdft/xcfunctionals.C','scfman/scfman.C','gesman/GuessMan.C']]
 manifest['staged']=a.stage
 if a.stage:
  HEAVY.mkdir(parents=True,exist_ok=True);(HEAVY/'tmp').mkdir(exist_ok=True)
 (ROOT/'manifests/step2_fixed_v3.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print('Staged' if a.stage else 'Prepared preview',len(manifest['cases']),'cases')
if __name__=='__main__':main()
