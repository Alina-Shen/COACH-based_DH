"""Hash-only freeze for two approved continuous diagnostics, no tests/solver."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    folder=ROOT/'revwb97m2/manifests/continuous_k14_v1'
    if folder.exists():raise ValueError('preserve existing freeze')
    prior=json.loads((ROOT/'revwb97m2/manifests/k14_diagnostic_v1/plan.json').read_text())
    hashes=dict(prior['code_hashes'])
    for name in ['scripts/continuous_k14_v1.py','scripts/freeze_continuous_k14_v1.py',
                 'tests/test_continuous_k14_v1.py','slurm/run_continuous_k14_v1.sh']:
        path=ROOT/'revwb97m2'/name;hashes[str(path.relative_to(ROOT))]=sha(path)
    plan=dict(schema_version=1,purpose='two_approved_continuous_diagnostics_not_MIO_acceptance',
        kinds=['fixed_scalars','relaxed_k14'],seconds_each=600,threads=16,memory_gib=32,wall_minutes=90,
        matrix_sha256=prior['matrix_sha256'],input_sha256=prior['input_sha256'],
        output_parent='/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/fitting/continuous_k14_v1',
        user_approved_scope=True,submission_authorized=False,code_hashes=hashes,
        policy='Preserve objective/linear constraints; change selection integrality only, plus fixed scalar support in first case. No fractional incumbent promotion; no automatic MIO retry.')
    folder.mkdir(parents=True)
    (folder/'plan.json').write_text(json.dumps(plan,indent=2,sort_keys=True)+'\n')
    draft=dict(plan_sha256=sha(folder/'plan.json'),commit=None,user_approved_submission=False,
        tests_passed=False,resource_review_passed=False,route=None,test_report=None,test_report_sha256=None)
    (folder/'release_draft.json').write_text(json.dumps(draft,indent=2,sort_keys=True)+'\n')
    print('Hash-only continuous freeze complete. Release disabled; no tests or solver.')


if __name__=='__main__':main()
