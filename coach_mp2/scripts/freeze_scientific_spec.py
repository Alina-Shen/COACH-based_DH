"""One-time Step 1 test, validation and hash publication; no chemistry/submission."""
import importlib.util
import io
import json
from pathlib import Path
import time
import unittest
import sys

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('validator',ROOT/'scripts/validate_scientific_spec.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)

def publish(relative,value):
    with v.confined(ROOT/relative,(v.CODE,)).open('x') as handle:
        json.dump(value,handle,indent=2,allow_nan=False);handle.write('\n')

def main():
    if (ROOT/'manifests/scientific_spec_v1.freeze.json').exists():
        raise ValueError('v1 already frozen; use validator or create a new version')
    pre=v.validate(require_freeze=False)
    if not pre['passed']:raise ValueError('Pre-freeze scientific validation failed')
    suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern='test_*.py')
    stream=io.StringIO();start=time.monotonic()
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    report={'passed':result.wasSuccessful(),'tests_run':result.testsRun,'failures':len(result.failures),
            'errors':len(result.errors),'skipped':len(result.skipped),'elapsed_seconds':time.monotonic()-start,
            'python':sys.version,'test_sha256':v.digest(ROOT/'tests/test_scientific_spec.py'),
            'validator_sha256':v.digest(ROOT/'scripts/validate_scientific_spec.py')}
    with (ROOT/'results/step1_tests.log').open('x') as handle:handle.write(stream.getvalue())
    publish('results/step1_tests.json',report)
    if not report['passed']:raise ValueError('Tests failed; no scientific freeze published')
    files=['configs/scientific_spec_v1.json','configs/step_index_v1.json',
           'manifests/step_index_v1.freeze.json','manifests/step1_sources_v1.json',
           'scripts/build_scientific_spec_v1.py','scripts/validate_scientific_spec.py',
           'scripts/freeze_scientific_spec.py','tests/test_scientific_spec.py',
           'docs/scientific_specification.md','docs/storage_layout.md',
           'results/step1_database_comparison.json','results/step1_inheritance_audit.json','results/step1_tests.json','results/step1_tests.log']
    publish('manifests/scientific_spec_v1.freeze.json',{'schema_version':1,'status':'frozen',
        'frozen_on':'2026-09-12','files':{f:v.digest(ROOT/f) for f in files},
        'scope':'scientific_specification_not_runtime_release','git_commit_performed':False})
    final=v.validate()
    publish('results/step1_validation.json',final)
    if not final['passed']:raise ValueError('Post-freeze verification failed')
    print(json.dumps({'step1_passed':True,'tests':result.testsRun,'checks':len(final['checks']),
                      'spec_sha256':final['spec_sha256'],'runtime_ready':False},indent=2))

if __name__=='__main__':main()
