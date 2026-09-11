"""Freeze new selective recovery and partial-source hashes, without testing/solving."""
from revwb97m2.scripts import selective_recovery_v1 as v


def main():
    c, root = v.c, v.ROOT
    c.require(not v.PLAN.parent.exists(), 'preserve existing freeze')
    v.policy.settings()
    hashes = dict(c.read(v.old.PLAN)['hashes'])
    paths = ['selective_grid_v1.py', 'configs/selective_recovery_v1.yaml',
        'scripts/selective_recovery_v1.py', 'scripts/freeze_selective_recovery_v1.py',
        'tests/test_selective_recovery_v1.py', 'slurm/run_selective_recovery_v1.sh',
        'manifests/expanded_validation_v1/plan.json', 'manifests/expanded_validation_v1/release_20260911.json',
        'results/2026-09-11-expanded-validation-tests.json',
        'results/2026-09-11-expanded-validation-25790995-audit.json']
    for name in paths:
        hashes['revwb97m2/' + name] = c.digest(root / 'revwb97m2' / name)
    name = 'coach/2_optimization/coachopt/select_diff_constraints.py'
    hashes[name] = c.digest(root / name)
    v.PLAN.parent.mkdir(parents=True)
    c.write(v.PLAN, dict(schema_version=1, schedule=v.schedule(), hashes=hashes,
        config_sha256=c.digest(v.policy.CONFIG), matrix_sha256=c.d.full.MATRIX_SHA,
        input_sha256=c.d.full.INPUT_SHA,
        source_root='/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/fitting/expanded_validation_v1/25790995',
        source_audit='revwb97m2/results/2026-09-11-expanded-validation-25790995-audit.json',
        output_parent='/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/fitting/selective_recovery_v1',
        seconds=600, threads=16, memory_gib=32, wall_minutes=45, bulk_authorized=False,
        acceptance='selected_constraints_only', full_grid_violations='report_for_user_review'))
    c.write(v.PLAN.parent / 'release_draft.json', dict(plan_sha256=c.digest(v.PLAN), commit=None,
        submission_authorized=False, tests_passed=False, resources_reviewed=False,
        test_report=None, test_report_sha256=None, route=None))
    print('Selective recovery frozen; release disabled; tests/solves not run.')


if __name__ == '__main__':
    main()
