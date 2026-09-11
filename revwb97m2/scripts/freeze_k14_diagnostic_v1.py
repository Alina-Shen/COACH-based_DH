"""Hash-only diagnostic pre-test freeze, no importing runner or executing tests."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    folder=ROOT/'revwb97m2/manifests/k14_diagnostic_v1'
    if folder.exists():raise ValueError('preserve diagnostic freeze')
    prior=json.loads((ROOT/'revwb97m2/manifests/full1498_mio_v1/plan.json').read_text())
    hashes=dict(prior['code_hashes'])
    for name in ['scripts/k14_diagnostic_v1.py','scripts/freeze_k14_diagnostic_v1.py',
                 'tests/test_k14_diagnostic_v1.py','slurm/run_k14_diagnostic_v1.sh',
                 'manifests/full1498_mio_v1/plan.json']:
        path=ROOT/'revwb97m2'/name;hashes[str(path.relative_to(ROOT))]=sha(path)
    plan=dict(schema_version=1,purpose='approved_diagnostic_not_six_solve_or_bulk_acceptance',
        budget=14,seconds=600,threads=16,memory_gib=32,wall_minutes=90,
        grid_candidates=[],start_policy='analytic_four_scalar_full_primal',
        matrix_sha256=prior['matrix_validation_sha256'],input_sha256=prior['input_manifest_sha256'],
        output_parent='/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/fitting/k14_diagnostic_v1',
        user_approved_scope=True,submission_authorized=False,code_hashes=hashes)
    folder.mkdir(parents=True)
    (folder/'plan.json').write_text(json.dumps(plan,indent=2,sort_keys=True)+'\n')
    release=dict(plan_sha256=sha(folder/'plan.json'),user_approved_submission=False,
        tests_passed=False,resource_review_passed=False,commit=None,route=None,
        test_report=None,test_report_sha256=None)
    (folder/'release_draft.json').write_text(json.dumps(release,indent=2,sort_keys=True)+'\n')
    print('Hash-only freeze and disabled release; no tests or license/solver execution.')


if __name__=='__main__':main()
