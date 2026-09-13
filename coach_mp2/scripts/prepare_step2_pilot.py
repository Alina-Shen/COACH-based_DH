from pathlib import Path
import hashlib,json,re,shutil,argparse
ROOT=Path(__file__).resolve().parents[1]
SCRATCH=Path('/clusterfs/mhg-data/yaoshen/scf_read/coach_mp2/step2_pilot_v1')
HEAVY=Path('/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2/step2_pilot_v1')
def record(p):return dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--stage',action='store_true');a=parser.parse_args()
 manifest={'cases':[],'scope':'two species; fixed-orbital evaluation and explicitly user-authorized SCF repeatability pilot','reference':'existing COACH fixture outputs; GSCDB Analysis has no COACH column','tolerance_hartree':2e-6}
 for species in ['SIE4x4_h2o','16_C_AE18']:
  source=Path('/clusterfs/mhg-data/yaoshen/GSCDB/qchem_inputs')/(species+'.in')
  text=source.read_text();text,n=re.subn(r'(?im)^method\s+\S+', 'METHOD COACH',text);assert n==1
  for mode in ['fixed','scf']:
   content=text
   if mode=='fixed':content,n=re.subn(r'(?im)^max_scf_cycles\s+\d+', 'MAX_SCF_CYCLES 0',content);assert n==1
   content=content.replace('$rem','$rem\nSCF_GUESS READ\nSCF_FINAL_PRINT 1',1)
   inp=ROOT/'inputs/step2_pilot_v1'/f'{species}_{mode}.in';inp.write_text(content)
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
 manifest['runtime']=[record(qc/p) for p in ['bin/qchem','build/qcprog.exe','libdft/xcfunctionals.C']]
 manifest['staged']=a.stage
 if a.stage:
  HEAVY.mkdir(parents=True,exist_ok=True);(HEAVY/'tmp').mkdir(exist_ok=True)
 (ROOT/'manifests/step2_pilot_v1.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print('Staged' if a.stage else 'Prepared preview',len(manifest['cases']),'cases')
if __name__=='__main__':main()
