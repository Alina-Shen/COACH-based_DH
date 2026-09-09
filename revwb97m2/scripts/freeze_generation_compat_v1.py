"""Hash-only preparation; no new validator execution, tests, orbital copies or jobs."""
import csv
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):return json.loads(Path(path).read_text())


def write(path,value):
    with Path(path).open('x') as f:json.dump(value,f,indent=2,sort_keys=True)


def main():
    folder=ROOT/'manifests/generation_compat_v1'
    if folder.exists():raise ValueError('preserve frozen compatibility package')
    native=ROOT/'manifests/production_generator/v7_canary_v1.json'
    old=read(native)['code_hashes'];addition=ROOT/'pilot100_inputs.py'
    assert all(sha(p)==h for p,h in old.items())
    top={str(p.resolve()) for p in ROOT.glob('*.py')}
    assert top-{p for p in old if Path(p).parent==ROOT}=={str(addition)}
    files=[ROOT/p for p in (
        'scripts/generation_compat_v1.py','scripts/corrected_canary_evidence_v2.py',
        'scripts/ecp21_inputs_v1.py','scripts/generate_training_features_v3.py',
        'scripts/freeze_generation_compat_v1.py','slurm/run_full_training_features_v3.sh',
        'tests/test_generation_compat_v1.py','tests/test_ecp21_inputs_v1.py')]
    authorities=[native,ROOT/'manifests/production_generator/corrected_canary_evidence_v1.json',
        ROOT/'manifests/production_generator/large_corrected_canaries_v1.json',
        ROOT/'results/2026-09-09-ecp21-production-reference-review.json']
    contract=dict(schema_version=1,native_plan=str(native),allowed_additions={str(addition):sha(addition)},
        authorities={str(p):sha(p) for p in authorities},implementation_hashes={str(p):sha(p) for p in files},
        status='untested_precommit',submission_authorized=False,
        policy='exact historical dependency bytes plus exactly the reviewed addition; no monkeypatch/historical rewrite')
    folder.mkdir(parents=True);write(folder/'contract.json',contract)
    auditpath=ROOT/'results/2026-09-09-full-training-next-generation-audit.json';audit=read(auditpath)
    reuse=set(audit['additional_canary_candidates_pending_contract_migration'])
    groups={}
    for case in audit['cases']:
        if not case['supported'] or case['species'] in reuse:continue
        groups.setdefault(str(case['memory_gib']),[]).append(case['species'])
    review=read(authorities[-1])
    draft=dict(schema_version=1,status='selection_only_not_native_execution_contract',submission_authorized=False,
        compatibility_contract_sha256=sha(folder/'contract.json'),source_audit_sha256=sha(auditpath),
        full_entries=1498,full_species=2799,already_accepted_species=224,
        reuse_candidates=sorted(reuse),ordinary_resource_groups={k:sorted(v) for k,v in groups.items()},
        embedded_ecp_gateway_candidates=[c['species'] for c in review['cases']],
        next_gate='user pre-test commit, tests and raw readbacks, resolve reuse, full source-tree hashes/resource/storage freeze; user release before jobs',
        concurrency_cap=None,forbidden_qos=['lr_lowprio'])
    write(folder/'full_training_selection_draft.json',draft)
    write(folder/'release_draft.json',dict(user_approved_submission=False,tests_passed=False,resource_review_passed=False,
        ecp_native_gateway_authorized=False,native_execution_plan=None,commit='USER_PRETEST_COMMIT_REQUIRED'))
    print('Hash-only freeze; ordinary selections', {k:len(v) for k,v in groups.items()},
          'reuse candidates',len(reuse),'ECP gateway candidates',len(review['cases']),'; NO tests or submission')


if __name__=='__main__':main()
