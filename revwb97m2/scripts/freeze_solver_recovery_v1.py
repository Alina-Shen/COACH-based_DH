"""Hash-only preparation; does not authorize submission or execute tests."""
from revwb97m2.scripts import solver_recovery_v1 as s


def main():
    c=s.c;root=s.ROOT;folder=s.PLAN.parent
    c.require(not folder.exists(),'preserve frozen plan')
    hashes=dict(c.read(c.PLAN)['code_hashes'])
    names=['scripts/continuous_readback_v2.py','tests/test_continuous_readback_v2.py',
        'scripts/solver_recovery_v1.py','scripts/freeze_solver_recovery_v1.py','tests/test_solver_recovery_v1.py',
        'slurm/run_solver_recovery_precision_v1.sh','slurm/run_solver_recovery_mio_v1.sh',
        'results/2026-09-11-continuous-v2-readback.json']
    for name in names:hashes['revwb97m2/'+name]=c.digest(root/'revwb97m2'/name)
    folder.mkdir(parents=True)
    c.write(s.PLAN,dict(schema_version=1,variants=s.VARIANTS,hashes=hashes,
        matrix_sha256=c.d.full.MATRIX_SHA,input_sha256=c.d.full.INPUT_SHA,
        source='/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/fitting/continuous_k14_v1/25783741',
        start_report='revwb97m2/results/2026-09-11-continuous-v2-readback.json',
        output_parent='/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/fitting/solver_recovery_v1',
        resources=dict(threads=16,memory_gib=32,precision_seconds_each=600,precision_wall_minutes=90,
                       mio_seconds=7200,mio_wall_minutes=180),
        bulk_authorized=False,policy='Independent precision and improved-start MIO diagnostics; no auto retry or promotion.'))
    c.write(folder/'release_draft.json',dict(plan_sha256=c.digest(s.PLAN),commit=None,
        submission_authorized=False,tests_passed=False,resources_reviewed=False,
        test_report=None,test_report_sha256=None,route=None))
    print('Frozen recovery plan; release disabled pending committed tests/resource review.')


if __name__=='__main__':main()
