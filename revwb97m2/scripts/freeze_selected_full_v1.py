"""Freeze full selected-pass plan without requiring unfinished discovery outputs."""
from revwb97m2 import selected_full_v1 as f


def freeze():
    p, r, g, root = f.e.check(f.DISCOVERY_RELEASE)
    names = ['revwb97m2/selected_full_v1.py', 'revwb97m2/selected_submit_v1.py',
        'revwb97m2/slurm/run_selected_full_v1.sh', 'revwb97m2/tests/test_selected_full_v1.py',
        'revwb97m2/scripts/freeze_selected_full_v1.py',
        str(f.e.PLAN.relative_to(f.old.ROOT)), str(f.DISCOVERY_RELEASE.relative_to(f.old.ROOT))]
    hashes = {**p['hashes'], **{n: f.old.c.digest(f.old.ROOT / n) for n in names}}
    f.PLAN.parent.mkdir(exist_ok=False)
    f.old.c.write(f.PLAN, dict(schema_version=1, hashes=hashes, graph=f.task_graph(),
        output_root='/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/fitting/selected_full_v1',
        source_discovery_arrays=[25796986, 25801134], wls_sessions=2, seconds=7200,
        cpus=16, memory_gib=32, grid_wall_minutes=30, selected_wall_minutes=150,
        submission_authorized=False, final_model_user_review=True))
    f.old.c.write(f.PLAN.parent / 'release_draft.json', dict(plan_sha256=f.old.c.digest(f.PLAN),
        commit=None, test_report=None, test_report_sha256=None, submission_authorized=False,
        tests_passed=False, resources_reviewed=False, wls_sessions_reserved_for_campaign=False,
        route=dict(partition='cm1', account='lr_qchem', qos='condo_qchem')))
    print('PASS138-source/414-solve plan frozen; release disabled')


if __name__ == '__main__':
    freeze()
