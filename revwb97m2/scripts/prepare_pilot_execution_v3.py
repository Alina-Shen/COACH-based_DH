"""Read-only pilot input/coverage audit; writes planning artifacts, never submits."""
import collections
import json
from pathlib import Path

from revwb97m2.scripts import generate_training_features_v2 as generation

v = generation.native
PLAN = v.ROOT/'manifests/production_generator/training_first16_v3.json'
OUTPUT = v.ROOT/'results/pilot_execution_v3'


def category(row, first, corrected):
    name = row['species']
    if name in first:
        return 'first16_frozen_not_launched'
    if name in corrected:
        return 'corrected_canary_validated'
    if row['coverage'] != 'no_feature_candidates':
        return 'legacy_candidate_requires_stage_migration'
    return 'new_generation_requires_frozen_execution_manifest'


def main():
    plan, settings = generation.load(PLAN)
    accepted = generation.corrected.validate_registry()
    first = {c['species'] for c in plan['cases']}
    pilot = v.read(generation.PILOT)
    records = []
    for row in pilot:
        source = Path(row['qchem_input_path'])
        v.require(v.digest(source) == row['qchem_input_sha256'], 'pilot input changed')
        orbital_root = v.ORBITALS/row['species']
        tree = [dict(path=str(p.relative_to(orbital_root)), bytes=p.stat().st_size)
                for p in sorted(orbital_root.rglob('*')) if p.is_file()]
        v.require(tree and (v.ORBITALS/row['species']/'qarchive.h5').is_file(), 'missing pilot restart')
        try:
            inputs = v.stage_inputs(source.read_text(), settings, row['basis_bridge'])
            input_gate_error = None
        except ValueError as exc:
            # Report unsupported chemistry explicitly; do not invent a conversion.
            inputs = {}
            input_gate_error = str(exc)
        records.append(dict(species=row['species'], category=category(row, first, accepted),
            resources={k: int(row[k]) for k in ('cpus', 'requested_memory_gib', 'wall_hours')},
            required_stages=list(inputs), input_gate_error=input_gate_error,
            input_sha256=row['qchem_input_sha256'],
            source_tree_metadata=tree, source_tree_bytes=sum(r['bytes'] for r in tree),
            orbital_integrity='tree metadata only; content validation required by execution freeze',
            historical_coverage=row['coverage'],
            candidates=[dict(path=p, exists=Path(p).is_file()) for p in row['artifact_candidates']],
            stage_reuse_status='accepted corrected full species' if row['species'] in accepted
                else 'not certified by this metadata/preparation audit'))
    summary = dict(species_count=len(records), categories=dict(collections.Counter(r['category'] for r in records)),
        remaining_after_first16=len(records)-len(first),
        remaining_resource_classes=dict(collections.Counter(
            str(r['resources']['requested_memory_gib'])+'GiB/'+str(r['resources']['cpus'])+'CPU'
            for r in records if r['species'] not in first)),
        pilot_sha256=v.digest(generation.PILOT), first16_plan_sha256=v.digest(PLAN),
        specification_sha256=settings.specification_sha256,
        all_seven_fresh_corrected_readbacks_passed=True,
        input_gate_blockers=[dict(species=r['species'], error=r['input_gate_error'])
                             for r in records if r['input_gate_error']],
        submission_authorized=False, stage_migration_complete=False,
        note='Planning only. Resource classes include reuse candidates; not a native-job count.')
    OUTPUT.mkdir(parents=True, exist_ok=True)
    v.write(OUTPUT/'remaining_pilot_preparation.json', dict(summary=summary, species=records))
    release = dict(schema_version=1, commit='USER_COMMIT_REQUIRED',
        plan_sha256=v.digest(PLAN), corrected_evidence_sha256=v.digest(generation.corrected.REGISTRY),
        user_approved_submission=True, resource_review_passed=False,
        approval_note='User approved initial checkpoint and wider preparation; refresh resources after commit.',
        max_concurrent_jobs=8, concurrency_enforcement='single Slurm array 0-15%8',
        scheduler_routes={c['species']: dict(partition='cm1', account='lr_qchem', qos='condo_qchem')
                          for c in plan['cases']})
    generation.reviewed_routes(plan, release)
    v.write(v.ROOT/'manifests/production_generator/training_first16_v3_release_draft.json', release)
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
