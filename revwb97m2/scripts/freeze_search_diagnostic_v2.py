"""Freeze metadata-only correction; preserve failed v1 artifacts and code."""
from revwb97m2.scripts import search_diagnostic_v2 as s


def main():
    c=s.c;folder=s.PLAN.parent;c.require(not folder.exists(),'preserve freeze')
    p=c.read(s.ROOT/'revwb97m2/manifests/search_diagnostic_v1/plan.json')
    p['hashes']=dict(p['hashes'])
    for name in ('scripts/search_diagnostic_v2.py','scripts/freeze_search_diagnostic_v2.py',
                 'tests/test_search_diagnostic_v2.py','slurm/run_search_diagnostic_v2.sh'):
        path='revwb97m2/'+name;p['hashes'][path]=c.digest(s.ROOT/path)
    p['output_parent']='/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/fitting/search_diagnostic_v2'
    p['change']='Metadata serialization of infinite NodeLimit only; same seven cases and science.'
    folder.mkdir(parents=True);c.write(s.PLAN,p)
    c.write(folder/'release_draft.json',dict(plan_sha256=c.digest(s.PLAN),commit=None,submission_authorized=False,
        tests_passed=False,resources_reviewed=False,test_report=None,test_report_sha256=None,route=None))
    print('V2 frozen; no retry authorized.')


if __name__=='__main__':main()
