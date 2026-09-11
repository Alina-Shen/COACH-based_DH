"""Prepare immutable diagnostic scope, never release or submit."""
from revwb97m2.scripts import search_diagnostic_v1 as s


def main():
    c=s.c;folder=s.PLAN.parent;c.require(not folder.exists(),'preserve plan')
    hashes=dict(c.read(s.old.PLAN)['hashes'])
    for name in ('scripts/search_diagnostic_v1.py','scripts/freeze_search_diagnostic_v1.py',
                 'tests/test_search_diagnostic_v1.py','slurm/run_search_diagnostic_v1.sh'):
        path='revwb97m2/'+name;hashes[path]=c.digest(s.ROOT/path)
    folder.mkdir(parents=True)
    c.write(s.PLAN,dict(schema_version=1,cases=s.CASES,support=list(s.SUPPORT),hashes=hashes,
        seconds_each=600,threads=16,memory_gib=32,wall_minutes=180,
        matrix_sha256=c.d.full.MATRIX_SHA,input_sha256=c.d.full.INPUT_SHA,
        start_report='revwb97m2/results/2026-09-11-continuous-v2-readback.json',
        output_parent='/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/fitting/search_diagnostic_v1',
        bulk_authorized=False,policy='Same science; controlled QP/root algorithms and independently audited fixed COACH-informed support. No fractional rounding or auto retry.'))
    c.write(folder/'release_draft.json',dict(plan_sha256=c.digest(s.PLAN),commit=None,submission_authorized=False,
        tests_passed=False,resources_reviewed=False,test_report=None,test_report_sha256=None,route=None))
    print('Hash-only freeze complete; submission disabled.')


if __name__=='__main__':main()
