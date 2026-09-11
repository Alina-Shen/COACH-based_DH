"""Freeze expanded validation overlay and accepted source identity, no tests/solve."""
from pathlib import Path
from revwb97m2.scripts import expanded_validation_v1 as v


def main():
    c=v.c;root=v.ROOT;folder=v.PLAN.parent;c.require(not folder.exists(),'preserve freeze')
    hashes=dict(c.read(v.a.e.PLAN)['hashes'])
    paths=['expanded_adapter.py','configs/expanded_validation_v1.yaml','scripts/expanded_validation_v1.py',
        'scripts/freeze_expanded_validation_v1.py','tests/test_expanded_validation_v1.py','slurm/run_expanded_validation_v1.sh',
        'manifests/expanded_objective_v1/release_20260911.json',
        'results/2026-09-11-expanded_objective_v1-tests.json']
    for name in paths:hashes['revwb97m2/'+name]=c.digest(root/'revwb97m2'/name)
    source=Path('/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/fitting/expanded_objective_v1/25787337')
    folder.mkdir(parents=True)
    c.write(v.PLAN,dict(schema_version=1,schedule=v.schedule(),hashes=hashes,config_sha256=c.digest(v.a.CONFIG),
        matrix_sha256=c.d.full.MATRIX_SHA,input_sha256=c.d.full.INPUT_SHA,source_root=str(source),
        source_publication_sha256=c.digest(source/'publication.json'),seconds=600,threads=16,memory_gib=32,wall_minutes=90,
        output_parent='/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/fitting/expanded_validation_v1',
        bulk_authorized=False,full_training_grid_advancement_gate=True))
    c.write(folder/'release_draft.json',dict(plan_sha256=c.digest(v.PLAN),commit=None,submission_authorized=False,
        tests_passed=False,resources_reviewed=False,test_report=None,test_report_sha256=None,route=None))
    print('Expanded six-stage validation frozen; release disabled.')


if __name__=='__main__':main()
