"""Read frozen input metadata with explicit user-approved basis amendments."""
from pathlib import Path
import csv,json,hashlib
R=Path(__file__).resolve().parents[1]
def load_rows():
 config=R/'configs/input_basis_amendments_v1.json'
 if not config.exists():return list(csv.DictReader((R/'manifests/step4_inputs_v1.csv').open()))
 d=json.loads(config.read_text());p=R/d['base_manifest'];assert hashlib.sha256(p.read_bytes()).hexdigest()==d['base_manifest_sha256']
 rows=list(csv.DictReader(p.open()));seen=set()
 for row in rows:
  name=row['species']
  if name in d['overrides']:
   item=d['input_overrides'][name];inp=R/item['path'];assert hashlib.sha256(inp.read_bytes()).hexdigest()==item['sha256']
   row.update(d['overrides'][name]);seen.add(name)
 assert seen==set(d['overrides'])
 return rows
