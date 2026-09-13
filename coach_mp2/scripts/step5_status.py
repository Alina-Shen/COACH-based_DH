"""Read-only import progress; counts atomic published records, never staging files."""
from pathlib import Path
import json,csv
ROOT=Path(__file__).resolve().parents[1]
DEST=Path('/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2/step5_import_v1')
def main():
 rows=list(csv.DictReader((ROOT/'manifests/step5_inventory_v1.csv').open()))
 expected={r['species'] for r in rows if r['status']!='missing'}
 published={p.name for p in (DEST/'species').iterdir() if (p/'import.json').is_file()} if (DEST/'species').exists() else set()
 assert published<=expected
 summary=dict(expected_available_imports=len(expected),atomically_published=len(published),remaining_available_imports=len(expected-published),special_native_gate_cases=[r['species'] for r in rows if r['status']=='quarantine'],missing=sum(r['status']=='missing' for r in rows),step5_complete=False)
 print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
