"""Freeze supported remaining pilot species; no submission and no legacy promotion."""
import argparse
from collections import defaultdict
from pathlib import Path
import tempfile

from revwb97m2.scripts import generate_training_features_v2 as g

ROOT = g.ROOT
AUDIT = ROOT/'results/pilot_execution_v3/remaining_pilot_preparation.json'
READBACK = ROOT/'results/pilot_execution_v3/first16_independent_readback_20260908.json'
FIRST = ROOT/'manifests/production_generator/training_first16_v3.json'
OUTPUT = ROOT/'manifests/production_generator/pilot_remaining_v3'


def select_groups(rows):
    names = [r['species'] for r in rows]
    g.native.require(len(names) == len(set(names)), 'duplicate inventory species')
    groups = defaultdict(list)
    for row in rows:
        if row['category'] != 'new_generation_requires_frozen_execution_manifest' or row['input_gate_error']:
            continue
        resources = row['resources']
        key = tuple(resources[k] for k in ('cpus', 'requested_memory_gib', 'wall_hours'))
        g.native.require(key in {(8, 14, 72), (8, 21, 72), (8, 35, 72), (16, 227, 336)},
                         'unreviewed resource class')
        groups[key].append(row['species'])
    return {key: sorted(value) for key, value in sorted(groups.items())}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--memory-gib', type=int, required=True, choices=(14, 21, 35, 227))
    args = parser.parse_args()
    audit, readback = g.native.read(AUDIT), g.native.read(READBACK)
    g.native.require(readback['passed'] and len(readback['cases']) == 16 and
                     all(c['passed'] for c in readback['cases']) and
                     readback['plan_sha256'] == g.native.digest(FIRST), 'first16 checkpoint not accepted')
    first, _ = g.load(FIRST)
    g.native.require({c['species'] for c in first['cases']} == {c['species'] for c in readback['cases']},
                     'wrong first16 readback cohort')
    g.native.require(audit['summary']['pilot_sha256'] == g.native.digest(g.PILOT), 'pilot selection changed')
    groups = select_groups(audit['species'])
    g.native.require(sum(map(len, groups.values())) == 166, 'unexpected supported pilot scope')
    (cpus, memory, hours), names = next((key, names) for key, names in groups.items() if key[1] == args.memory_gib)
    g.native.require(not set(names) & {c['species'] for c in first['cases']}, 'first16 regeneration forbidden')
    namespace = f'pilot_remaining_v3_m{memory}'
    OUTPUT.mkdir(parents=True, exist_ok=True)
    final = OUTPUT/f'{namespace}.json'
    draft = OUTPUT/f'{namespace}_release_draft.json'
    g.native.require(not final.exists() and not draft.exists(), 'refusing to overwrite frozen manifest')
    print(f'Freezing {len(names)} species: {cpus} CPU / {memory} GiB / {hours} h', flush=True)
    with tempfile.TemporaryDirectory(prefix='pilot-freeze-') as temporary:
        plan = g.freeze(Path(temporary)/'plan.json', names, namespace)
    g.native.require(all(c['resources'] == dict(cpus=cpus, requested_memory_gib=memory, wall_hours=hours)
                         for c in plan['cases']), 'resource grouping disagrees with authoritative inventory')
    plan['concurrency_proposal'] = None
    plan['concurrency_policy'] = 'User removed eight-task cap; no percent array throttle. Scheduler limits apply.'
    plan['preparation_authorities'] = {str(p):g.native.digest(p) for p in (Path(__file__), AUDIT, READBACK)}
    g.native.write(final, plan)
    g.load(final)
    # Routing is release metadata, not an alteration of frozen scientific inputs.
    # Current review favors cm1 for ordinary jobs; lr8 isolates the high-memory pair.
    route = dict(partition='lr8', account='lr_mhg2', qos='mhg2_lr8_normal') if memory == 227 else \
            dict(partition='cm1', account='lr_qchem', qos='condo_qchem')
    release = dict(schema_version=1, commit='USER_COMMIT_REQUIRED',
        plan_sha256=g.native.digest(final), corrected_evidence_sha256=g.native.digest(g.corrected.REGISTRY),
        user_approved_submission=False, resource_review_passed=False,
        scheduler_routes={name:route for name in names}, max_concurrent_jobs=None,
        concurrency_enforcement=f'--array=0-{len(names)-1}; no percent throttle',
        note='Precommit draft only. Refresh live routing/resources and create an actual release before submission.')
    g.reviewed_routes(plan, release)
    g.native.write(draft, release)
    g.native.write(OUTPUT/f'{namespace}_summary.json', dict(
        species=names, count=len(names), cpus=cpus, memory_gib=memory, wall_hours=hours,
        stages=sum(len(c['stages']) for c in plan['cases']),
        minimum_copy_bytes=plan['minimum_copy_bytes'],
        storage_free_bytes_at_freeze=plan['storage_free_bytes_at_freeze'],
        plan_sha256=g.native.digest(final), route_proposal=route,
        required_sbatch_overrides=[f'--array=0-{len(names)-1}', f'--cpus-per-task={cpus}',
                                  f'--mem={memory}G', f'--time={hours}:00:00',
                                  *[f'--{k}={v}' for k,v in route.items()]],
        launcher=str(g.ARRAY_LAUNCHER), plan=str(final), release_draft=str(draft),
        submission_authorized=False))
    print(f'PASS frozen/loaded {final}; {plan["minimum_copy_bytes"]} minimum copy bytes; NOT submitted', flush=True)


if __name__ == '__main__':
    main()
