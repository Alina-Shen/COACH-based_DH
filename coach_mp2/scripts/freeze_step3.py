"""One-shot Step 3 artifact freeze, independent of any optimization backend."""
from pathlib import Path
import hashlib,json
from validate_step3_roles import audit
ROOT=Path(__file__).resolve().parents[1]
def main():
 target=ROOT/'manifests/step3_freeze_v1.json'
 if target.exists():raise FileExistsError('Step 3 already frozen')
 audit()
 metrics=json.loads((ROOT/'results/step3_metrics_validation.json').read_text());assert metrics['passed']
 log=(ROOT/'results/step3_tests.log').read_text();assert 'Ran 18 tests' in log and log.rstrip().endswith('OK')
 files=list((ROOT/'manifests/data_roles_v1').rglob('*'))
 files += [ROOT/p for p in ['scripts/build_step3_roles.py','scripts/validate_step3_roles.py','scripts/step3_metrics.py','scripts/validate_step3_metrics.py','scripts/freeze_step3.py','scripts/check_step2_workbook_reference.py','tests/test_step3.py','results/step3_tests.log','results/step3_metrics_validation.json','results/step3_complete.md']]
 pins={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files) if p.is_file()}
 with target.open('x') as f:json.dump({'schema_version':1,'step':3,'status':'frozen','date':'2026-09-12','sha256':pins},f,indent=2);f.write('\n')
 print('Frozen',len(pins),'artifacts')
if __name__=='__main__':main()
