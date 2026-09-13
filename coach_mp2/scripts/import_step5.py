"""Resumable verified immutable import of structurally eligible legacy records.
Top-level scratch files only; nested fragment jobs are not parent restart data.
No quantum chemistry, overwrite, or fallback to another functional.
"""
from pathlib import Path
import csv,json,hashlib,os,concurrent.futures
ROOT=Path(__file__).resolve().parents[1]
DEST=Path('/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2/step5_import_v1')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
def one(row):
 name=row['species'];assert '/' not in name and name not in ('.','..')
 source=Path(row['source']);target=DEST/'species'/name
 if target.exists():
  record=json.loads((target/'import.json').read_text())
  for fn,h in record['sha256'].items():assert sha(target/fn)==h==sha(source/fn)
  return record
 stage=DEST/'staging'/name;stage.mkdir(parents=True,exist_ok=True)
 files=sorted(f for f in source.iterdir() if f.is_file() and not f.is_symlink())
 hashes={}
 for f in files:
  before=f.stat();out=stage/f.name
  h=hashlib.sha256()
  with f.open('rb') as a,out.open('wb') as b:
   for chunk in iter(lambda:a.read(4*1024*1024),b''):h.update(chunk);b.write(chunk)
   b.flush();os.fsync(b.fileno())
  after=f.stat();assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns),'source changed'
  digest=h.hexdigest();assert sha(out)==digest;hashes[f.name]=digest
 record=dict(species=name,source=str(source),sha256=hashes,excluded_nested_directories=sorted(f.name for f in source.iterdir() if f.is_dir()),status='verified_copy_structural_only',numerical_validation_pending=True,basis_identity_pending=True)
 (stage/'import.json').write_text(json.dumps(record,indent=2)+'\n')
 for f in stage.iterdir():f.chmod(0o444)
 target.parent.mkdir(parents=True,exist_ok=True);stage.rename(target)
 return record

def main():
 rows=list(csv.DictReader((ROOT/'manifests/step5_inventory_v1.csv').open()));selected=[r for r in rows if r['status']=='structural_pass']
 DEST.mkdir(parents=True,exist_ok=True)
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  for i,r in enumerate(pool.map(one,selected)):
   if (i+1)%100==0:print('Published',i+1,'/',len(selected),flush=True)
 report=dict(imported=len(selected),destination=str(DEST),scope='top-level native restart and archive files, structurally passing available species only',complete_step5=False)
 (ROOT/'results/step5_import_v1.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()
