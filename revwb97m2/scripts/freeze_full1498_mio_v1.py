"""Hash-only pre-test freeze; does not import or execute the new runner/tests."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    folder=ROOT/'revwb97m2/manifests/full1498_mio_v1'
    if (folder/'plan.json').exists() or (folder/'release_draft.json').exists():
        raise ValueError('preserve existing freeze')
    proposal=json.loads((folder/'proposal.json').read_text())
    files=list((ROOT/'revwb97m2').glob('*.py'))+[
        ROOT/'revwb97m2'/name for name in (
            'scripts/run_v7_fit.py','scripts/test_v7_end_to_end.py','scripts/run_pilot100_fit_v1.py',
            'scripts/full1498_mio_v1.py','scripts/freeze_full1498_mio_v1.py',
            'scripts/assemble_full1498_v1.py','scripts/assemble_pilot100_v1.py',
            'scripts/audit_full1498_matrix_v1.py','scripts/prepare_training_preflight.py',
            'scripts/generate_training_features_v3.py','scripts/corrected_canary_evidence_v2.py',
            'slurm/run_full1498_mio_v1.sh','tests/test_full1498_mio_v1.py',
            'configs/scientific_spec.yaml','configs/archive/scientific_spec.v6.yaml',
            'environment/conda-linux-64.explicit.txt','environment/pip-linux-64.lock.txt',
            'manifests/full1498_mio_v1/proposal.json')]
    plan=dict(schema_version=1,purpose='approved_bounded_full1498_not_bulk',schedule=proposal['schedule'],
        seconds=600,threads=16,memory_gib=32,wall_minutes=90,
        user_approved_scope=True,approval_date='2026-09-11',submission_authorized=False,
        full_training_grid_advancement_gate=True,pretest_commit_required=True,
        output_parent='/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/fitting/full1498_mio_v1',
        matrix_validation_sha256=proposal['matrix_validation_sha256'],
        input_manifest_sha256=proposal['input_manifest_sha256'],
        specification_sha256=sha(ROOT/'revwb97m2/configs/scientific_spec.yaml'),
        code_hashes={str(p.relative_to(ROOT)):sha(p) for p in sorted(set(files))})
    (folder/'plan.json').write_text(json.dumps(plan,indent=2,sort_keys=True)+'\n')
    draft=dict(plan_sha256=sha(folder/'plan.json'),commit='USER_PRETEST_COMMIT_REQUIRED',
        user_approved_submission=False,resource_review_passed=False,tests_passed=False,
        test_report=None,test_report_sha256=None,route=None,
        note='Scope approved; committed passing tests and live partition/resource review required; no bulk approval.')
    (folder/'release_draft.json').write_text(json.dumps(draft,indent=2,sort_keys=True)+'\n')
    print('Hash-only full1498 freeze; disabled release. No tests, WLS, solves or submission.')


if __name__=='__main__':main()
