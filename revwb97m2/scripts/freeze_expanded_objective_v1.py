"""Freeze matched big-M objective diagnostic without tests or execution."""
from revwb97m2.scripts import expanded_objective_v1 as e


def main():
    c=e.c;folder=e.PLAN.parent;c.require(not folder.exists(),'preserve freeze')
    hashes=dict(c.read(e.base.PLAN)['hashes'])
    for name in ('scripts/expanded_objective_v1.py','scripts/freeze_expanded_objective_v1.py',
                 'tests/test_expanded_objective_v1.py','slurm/run_expanded_objective_v1.sh'):
        path='revwb97m2/'+name;hashes[path]=c.digest(e.ROOT/path)
    folder.mkdir(parents=True)
    c.write(e.PLAN,dict(schema_version=1,cases=list(e.CASES),hashes=hashes,
        matrix_sha256=c.d.full.MATRIX_SHA,input_sha256=c.d.full.INPUT_SHA,
        start_report='revwb97m2/results/2026-09-11-continuous-v2-readback.json',
        output_parent='/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/fitting/expanded_objective_v1',
        selection='big_M',seconds_each=600,threads=16,memory_gib=32,wall_minutes=90,
        objective_normalization='full_SSE',bulk_authorized=False,
        policy='Same big-M feasible set and ridge; expanded objective diagnostic only. SOS1 deferred, no production switch.'))
    c.write(folder/'release_draft.json',dict(plan_sha256=c.digest(e.PLAN),commit=None,submission_authorized=False,
        tests_passed=False,resources_reviewed=False,test_report=None,test_report_sha256=None,route=None))
    print('Frozen expanded comparison; release disabled.')


if __name__=='__main__':main()
