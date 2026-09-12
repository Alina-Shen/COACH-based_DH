"""Freeze additive production execution identities, with all release gates disabled."""
from revwb97m2 import production_multistart_v1 as r


def freeze():
    g = r.graph()
    inherited = r.c.read(r.v.PLAN)['hashes']
    for name, sha in inherited.items():
        r.c.require(r.c.digest(r.ROOT / name) == sha, 'inherited source changed')
    names = [str(r.v.PLAN.relative_to(r.ROOT)), str(r.GRAPH.relative_to(r.ROOT)),
        'revwb97m2/production_multistart_plan_v1.py', 'revwb97m2/production_multistart_v1.py',
        'revwb97m2/production_submit_v1.py', 'revwb97m2/selective_readback_v2.py',
        'revwb97m2/configs/production_multistart_v1.proposal.yaml',
        'revwb97m2/slurm/run_production_multistart_v1.sh',
        'revwb97m2/tests/test_production_execution_v1.py',
        'revwb97m2/tests/test_production_multistart_plan_v1.py',
        'revwb97m2/scripts/freeze_production_execution_v1.py']
    hashes = {**inherited, **{n: r.c.digest(r.ROOT / n) for n in names}}
    r.PLAN.parent.mkdir(exist_ok=False)
    r.c.write(r.PLAN, dict(schema_version=1, graph_sha256=r.c.digest(r.GRAPH), hashes=hashes,
        output_parent='/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/fitting/production_multistart_v1',
        solves=len(g['tasks']), seconds_per_solve=7200, threads=16, memory_gib=32,
        wls_concurrent_sessions=2,
        solve_wall_minutes=150, grid_wall_minutes=30, production_executor_implemented=True,
        selected_constraints_only=True, final_model_user_review=True, submission_authorized=False))
    r.c.write(r.PLAN.parent / 'release_draft.json', dict(schema_version=1,
        plan_sha256=r.c.digest(r.PLAN), commit=None, test_report=None, test_report_sha256=None,
        submission_authorized=False, tests_passed=False, resources_reviewed=False, prebulk_approved=False,
        wls_sessions_reserved_for_campaign=False,
        run_name='review_pending', route=dict(partition='cm1', account='lr_qchem', qos='condo_qchem'),
        note='Route is a preview placeholder, not live resource review. Do not submit this draft.'))
    print('PASS frozen; production release disabled')


if __name__ == '__main__':
    freeze()
