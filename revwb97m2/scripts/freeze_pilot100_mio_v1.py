"""Hash-only pre-test freeze: does not import the new implementation or run tests."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    folder=ROOT/'revwb97m2/manifests/pilot100_mio_v1'
    if folder.exists():raise ValueError('preserve frozen plan; use a reviewed new version')
    files=list((ROOT/'revwb97m2').glob('*.py'))+[
        ROOT/'revwb97m2'/name for name in (
            'scripts/run_v7_fit.py','scripts/test_v7_end_to_end.py','scripts/run_pilot100_fit_v1.py',
            'scripts/pilot100_mio_v1.py','scripts/freeze_pilot100_mio_v1.py','scripts/assemble_pilot100_v1.py',
            'slurm/run_pilot100_mio_v1.sh','tests/test_pilot100_mio.py',
            'configs/scientific_spec.yaml','configs/archive/scientific_spec.v6.yaml',
            'environment/conda-linux-64.explicit.txt','environment/pip-linux-64.lock.txt')]
    candidates=['discovery14','discovery40']
    schedule=[dict(name=f'discovery{k}',budget=k,start=None,candidates=[]) for k in (14,40)]+[
        row for k in (14,40) for row in (
            dict(name=f'constrained{k}',budget=k,start=f'discovery{k}',candidates=candidates),
            dict(name=f'restart{k}',budget=k,start=f'constrained{k}',candidates=candidates))]
    plan=dict(schema_version=1,purpose='approved_bounded_pilot_not_bulk',schedule=schedule,
        seconds=300,threads=16,memory_gib=16,wall_minutes=45,
        user_approved_scope=True,submission_authorized=False,pretest_commit_required=True,
        output_parent='/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/fitting/pilot100_mio_v1',
        matrix_validation_sha256='4e22fc55ed9c78609865463c5e08fdef0283abc07d07112dfb508b3fe4791f18',
        specification_sha256=sha(ROOT/'revwb97m2/configs/scientific_spec.yaml'),
        code_hashes={str(p.relative_to(ROOT)):sha(p) for p in sorted(set(files))})
    folder.mkdir(parents=True)
    (folder/'plan.json').write_text(json.dumps(plan,indent=2,sort_keys=True)+'\n')
    draft=dict(plan_sha256=sha(folder/'plan.json'),commit='USER_PRETEST_COMMIT_REQUIRED',
        user_approved_submission=False,resource_review_passed=False,tests_passed=False,
        test_report=None,test_report_sha256=None,route=dict(partition='cm1',account='lr_qchem',qos='condo_qchem'),
        note='Scope approved; live resource review and passing committed test evidence required before release.')
    (folder/'release_draft.json').write_text(json.dumps(draft,indent=2,sort_keys=True)+'\n')
    print('Wrote hash-only freeze and DISABLED draft; no tests, adapter publication, WLS or submission.')


if __name__=='__main__':main()
