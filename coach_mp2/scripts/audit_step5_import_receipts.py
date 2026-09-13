"""Audit publication receipts; per-file byte readback was performed by importer."""
from pathlib import Path
import json,csv,hashlib,concurrent.futures,struct
from active_input_authority import load_rows
R=Path(__file__).resolve().parents[1];D=Path('/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2/step5_import_v1/species')
def audit(row):
 name=row['species'];p=D/name;f=p/'import.json';data=f.read_bytes();record=json.loads(data);assert record['species']==name
 expected=('/global/scratch/users/jsliang/BigNC/COACH/' if row['scope']=='BigNC_external' else '/global/scratch/users/jsliang/COACH3/')+name;assert record['source']==expected
 assert record['status']=='verified_copy_structural_only';assert {'53.0','54.0','58.0','819.0','99.0','molecule'}<=set(record['sha256'])
 for fn,h in record['sha256'].items():
  assert '/' not in fn and len(h)==64 and all(c in '0123456789abcdef' for c in h)
  q=p/fn;assert q.is_file() and not q.is_symlink() and q.stat().st_mode&0o222==0
 n,m,*_=struct.unpack('<4i',(p/'819.0').read_bytes());assert n==int(row['orbital_spherical_aos']) and 0<m<=n
 assert (p/'54.0').stat().st_size==16*n*n
 mo=(p/'53.0').stat().st_size;assert mo==16*m*(n+1) or (name in ['He3_47','He3_48','He3_49'] and mo==1592640 and n==315 and m==314)
 return dict(species=name,receipt_sha256=hashlib.sha256(data).hexdigest(),files=len(record['sha256']),bytes=sum((p/k).stat().st_size for k in record['sha256']))
def main():
 rows=[r for r in load_rows() if r['scope']!='GDB9_W1_F12_external'];assert len(rows)==14081
 assert {p.name for p in D.iterdir()}=={r['species'] for r in rows}
 assert not list((D.parent/'staging').iterdir())
 results=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  for i,r in enumerate(pool.map(audit,rows)):
   results.append(r)
   if (i+1)%2000==0:print('Audited receipts',i+1,flush=True)
 with (R/'manifests/step5_import_receipts_v1.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(results[0]));w.writeheader();w.writerows(results)
 report=dict(passed=True,available_species=14081,files=sum(x['files'] for x in results),bytes=sum(x['bytes'] for x in results),receipt_manifest_sha256=hashlib.sha256((R/'manifests/step5_import_receipts_v1.csv').read_bytes()).hexdigest(),verification='Each file was SHA256 checked during source streaming and destination readback before atomic publication; this audit independently checks receipts, coverage, permissions and dimensions, not another full 805GB hash scan.',gdb9_deferred=3371,native_readiness='separate six-case gate',historical_basis_identity='Not proven by header dimensions')
 (R/'results/step5_import_audit.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()
