"""Freeze additional discovery tasks; preserve all original production identities."""
from revwb97m2 import discovery_extension_v1 as e


def freeze():
    p, r, g, root = e.old.check(e.OLD_RELEASE)
    names = ['revwb97m2/discovery_extension_v1.py',
        'revwb97m2/slurm/run_discovery_extension_v1.sh',
        'revwb97m2/tests/test_discovery_extension_v1.py',
        'revwb97m2/scripts/freeze_discovery_extension_v1.py',
        str(e.old.PLAN.relative_to(e.old.ROOT)), str(e.OLD_RELEASE.relative_to(e.old.ROOT))]
    hashes = {**p['hashes'], **{n: e.old.c.digest(e.old.ROOT / n) for n in names}}
    e.PLAN.parent.mkdir(exist_ok=False)
    e.old.c.write(e.PLAN, dict(schema_version=1, hashes=hashes, additional_tasks=e.additional_tasks(),
        output_root='/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/fitting/discovery_extension_v1',
        existing_discovery_array=25796986, existing_candidates=14, additional_candidates=124,
        combined_candidates=138, grid_selection_submitted=False, selected_fits_submitted=False,
        noise_order='preserve existing seven-K draws, then ascending missing K', submission_authorized=False))
    e.old.c.write(e.PLAN.parent / 'release_draft.json', dict(plan_sha256=e.old.c.digest(e.PLAN),
        commit=None, test_report=None, test_report_sha256=None, submission_authorized=False,
        tests_passed=False, resources_reviewed=False, wls_sessions_reserved_for_campaign=False,
        route=dict(partition='cm1', account='lr_qchem', qos='condo_qchem')))
    print('PASS frozen124 additional tasks; release disabled')


if __name__ == '__main__':
    freeze()
