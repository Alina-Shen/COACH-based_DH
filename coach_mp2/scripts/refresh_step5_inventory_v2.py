from pathlib import Path
import csv,json,hashlib,concurrent.futures,collections
from inventory_step5 import audit
from active_input_authority import load_rows
R=Path(__file__).resolve().parents[1]
def main():
 rows=load_rows();cases={c['species']:c for c in json.loads((R/'manifests/step5_he3_v1.json').read_text())['cases']};out=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  for i,x in enumerate(pool.map(audit,rows)):
   if x['species'] in cases:
    p=Path(x['source'])/'53.0';expected=cases[x['species']]['source_hashes']['53.0']
    assert x['issues']=='53.0_size' and p.stat().st_size==1592640 and hashlib.sha256(p.read_bytes()).hexdigest()==expected
    x['status']='structural_pass_known_trailing_bytes';x['issues']='Known 5056 trailing bytes preserved; native invariant gate separately required'
   out.append(x)
   if (i+1)%2000==0:print('Audited',i+1,flush=True)
 with (R/'manifests/step5_inventory_v2.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
 report=dict(total=len(out),status=dict(collections.Counter(x['status'] for x in out)),basis_amendment='configs/input_basis_amendments_v1.json',gdb9='deferred before Step17, not current development blocker',prior_inventory_preserved=True)
 (R/'results/step5_inventory_v2.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()
