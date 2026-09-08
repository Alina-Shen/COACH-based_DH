"""Read-only source audit and deterministic, non-executable 100-entry proposal."""
import argparse
import csv
import hashlib
import json
import math
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = Path('/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2')


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def rows(path):
    with Path(path).open() as stream:
        return list(csv.DictReader(stream))


def unique(records, key):
    result = {r[key]: r for r in records}
    if len(result) != len(records):
        raise ValueError('duplicate ' + key)
    return result


def stoichiometry(value):
    fields = value.split(',')
    if not fields or len(fields) % 2:
        raise ValueError('invalid stoichiometry')
    terms = [{'coefficient': float(c), 'species': s}
             for c, s in zip(fields[::2], fields[1::2])]
    if any(not t['species'] or not math.isfinite(t['coefficient']) or
           t['coefficient'] == 0 for t in terms):
        raise ValueError('invalid stoichiometric term')
    return terms


def select_pilot(entries, seed_ids, inventory, ready, count=100):
    """Keep seeds, cover SI groups, then balance class representation/cost."""
    by_id = unique(entries, 'reaction')
    selected = [by_id[n] for n in seed_ids]
    if len(set(seed_ids)) != len(seed_ids) or len(selected) > count:
        raise ValueError('invalid seeds')
    chosen = set(seed_ids)
    covered = set(ready)
    for r in selected:
        covered.update(r['species'])

    def cost(r):
        new = set(r['species']) - covered
        return (max((int(inventory[s]['requested_memory_gib']) for s in new), default=0),
                sum(int(inventory[s]['orbital_aos']) ** 3 for s in new),
                len(new), int(r['global_index']))

    def add(r):
        selected.append(r)
        chosen.add(r['reaction'])
        covered.update(r['species'])

    for group in sorted({r['si_row_index'] for r in entries}, key=int):
        if not any(r['si_row_index'] == group for r in selected):
            add(min((r for r in entries if r['si_row_index'] == group), key=cost))
    if len(selected) > count:
        raise ValueError('group coverage exceeds pilot size')
    totals = Counter(r['property_class'] for r in entries)
    while len(selected) < count:
        taken = Counter(r['property_class'] for r in selected)
        available = [r for r in entries if r['reaction'] not in chosen]
        if not available:
            raise ValueError('insufficient entries')
        add(min(available, key=lambda r: (taken[r['property_class']] /
                                          totals[r['property_class']], cost(r))))
    return sorted(selected, key=lambda r: int(r['global_index']))


def publication(root, plan_hash, spec_hash, marker, recovery=None):
    """Check recorded evidence, not a fresh native/scalar numerical reparse."""
    if not (root / 'species.json').is_file():
        return {'status': 'no_publication'}
    try:
        p = read(root / 'species.json')
        if p['plan_sha256'] != plan_hash or p['specification_sha256'] != spec_hash:
            raise ValueError('stale plan/specification')
        if not p['artifacts'] or not all(digest(root / f) == h for f, h in p['artifacts'].items()):
            raise ValueError('artifact hash mismatch')
        if recovery and (recovery / 'recovery.json').is_file():
            q = read(recovery / 'recovery.json')
            if not (q['passed'] and q['species'] == root.name and q['checks'] and
                    all(q['checks'].values()) and q['plan_sha256'] == plan_hash and
                    q['specification_sha256'] == spec_hash and
                    q['d4_tolerance_hartree'] == 1e-12 and
                    q['recovery_code_sha256'] == digest(ROOT/'scripts/recover_v7_canary_d4.py') and
                    (recovery / 'RECOVERY_COMPLETE').read_text().strip() == digest(recovery / 'recovery.json') and
                    all(digest(f) == h for f, h in q['artifacts'].items())):
                raise ValueError('recovery evidence mismatch')
            status = 'recovery_evidence_hash_verified'
        elif (root / marker).is_file():
            status = 'completion_evidence_hash_verified'
        else:
            return {'status': 'publication_without_accepted_completion', 'root': str(root)}
        return {'status': status, 'root': str(root), 'publication_sha256': digest(root/'species.json')}
    except (OSError, ValueError, KeyError) as error:
        return {'status': 'evidence_failure', 'root': str(root), 'error': str(error)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    sources = {k: ROOT / v for k, v in {
        'entries': 'manifests/weights/coach_si_table2_final_cycle_entries.csv',
        'dataset': 'manifests/gscdb137/source/DatasetEval.csv',
        'roles': 'manifests/data_roles/reaction_roles.csv',
        'inventory': 'manifests/step12/step12_fitting_inventory_v1.csv',
        'bridge': 'manifests/basis_bridge/resolved_basis_records.csv',
        'refresh': 'manifests/reaction_features/v7_refresh_plan_v1.json',
        'canary': 'manifests/production_generator/v7_canary_v1.json',
        'spec': 'configs/scientific_spec.yaml',
    }.items()}
    entries = rows(sources['entries'])
    unique(entries, 'reaction')
    dataset = unique(rows(sources['dataset']), 'Reaction')
    roles = unique(rows(sources['roles']), 'reaction')
    inventory = unique(rows(sources['inventory']), 'species')
    bridges = unique(rows(sources['bridge']), 'species')
    errors = []
    reactions = []
    for index, entry in enumerate(entries, 1):
        r = dataset[entry['reaction']]
        role = roles[entry['reaction']]
        terms = stoichiometry(r['Stoichiometry'])
        w = float(entry['objective_weight'])
        checks = [int(entry['global_index']) == index,
                  r['Dataset'] == entry['dataset_eval_dataset'],
                  role['coefficient_fitting'] == 'true', role['final_assessment'] == 'false',
                  float(role['objective_weight']) == w, math.isfinite(w) and w > 0,
                  math.isfinite(float(r['Reference']))]
        if not all(checks):
            errors.append({'reaction': entry['reaction'], 'error': 'metadata/role/weight check'})
        reactions.append(dict(entry, objective_weight=w, reference_hartree=float(r['Reference']),
                              stoichiometry=terms, species=sorted({t['species'] for t in terms})))
    closure = {s for r in reactions for s in r['species']}
    if len(entries) != 1498 or len(closure) != 2799 or closure != set(inventory):
        errors.append({'error': 'training count/species closure mismatch'})

    refresh, canary = read(sources['refresh']), read(sources['canary'])
    evidence = {}
    for plan, key, marker in [(refresh, 'refresh', 'REFRESH_COMPLETE'), (canary, 'canary', 'CANARY_COMPLETE')]:
        for case in plan['cases']:
            name = case['species']
            rec = DATA / 'species/v7_canary_d4_recovery_v1' / name if key == 'canary' else None
            evidence[name] = publication(Path(plan['output_root']) / ('species' if key == 'refresh' else '') / name,
                                         digest(sources[key]), digest(sources['spec']), marker, rec)
    ready = {s for s, e in evidence.items() if e['status'].endswith('hash_verified')}
    # Path-only scan: old/partial arrays are candidates, never silently promoted.
    files = subprocess.check_output(['rg', '--files', str(DATA)], text=True).splitlines()
    candidates = {s: [] for s in closure}
    for name in files:
        p = Path(name)
        if p.name in ('feature_vector_292.npy', 'semilocal_features_288.npy', 'scalar_manifest.json', 'fixed_energy.json'):
            for species in set(p.parts) & closure:
                candidates[species].append(name)
    species_rows = []
    for name in sorted(closure):
        r = inventory[name]
        input_path = Path(r['qchem_input_path'])
        input_ok = input_path.is_file() and digest(input_path) == r['qchem_input_sha256']
        bridge = bridges.get(name, {})
        bridge_ok = (bridge.get('qchem_source_input_sha256') == r['qchem_input_sha256'] and
                     bridge.get('source_record_sha256') == r['source_record_sha256'] and
                     bridge.get('runnable_status') == 'runnable_basis_metadata_validated')
        if not input_ok or not bridge_ok:
            errors.append({'species': name, 'error': 'input hash or basis bridge identity/status'})
        archive = Path('/clusterfs/mhg-data/yaoshen/scf_read/wb97m_os_rimp2') / name / 'qarchive.h5'
        stages_root = Path(canary['output_root']) / name / 'stages'
        stage_markers = sorted(str(p) for p in stages_root.glob('*/STAGE_COMPLETE.json'))
        species_rows.append(dict(r, input_hash_verified=input_ok, basis_bridge_identity_verified=bridge_ok,
            basis_bridge=bridges.get(name), orbital_candidate=str(archive),
            orbital_candidate_exists=archive.is_file(),
            orbital_bytes=archive.stat().st_size if archive.is_file() else None,
            orbital_integrity_checked=False, artifact_candidates=sorted(candidates[name]),
            canary_stage_markers_present=stage_markers,
            publication_evidence=evidence.get(name, {'status': 'no_registered_v7_publication'}),
            coverage='recorded_v7_evidence_verified' if name in ready else
                     'unvalidated_or_legacy_candidates' if candidates[name] else 'no_feature_candidates'))
    for r in reactions:
        r['species_without_verified_v7_evidence'] = sorted(set(r['species']) - ready)
    seed_ids = [r['reaction'] for r in refresh['reactions']]
    pilot = select_pilot(reactions, seed_ids, inventory, ready)
    pilot_species = {s for r in pilot for s in r['species']}
    def summary(selected, names):
        return dict(entries=len(selected), species=len(names),
                    entries_with_verified_species_evidence=sum(not r['species_without_verified_v7_evidence'] for r in selected),
                    species_with_verified_v7_evidence=len(names & ready),
                    species_requiring_generation_or_validation=len(names - ready),
                    si_groups=len({r['si_row_index'] for r in selected}),
                    property_classes=dict(Counter(r['property_class'] for r in selected)),
                    species_memory_gib=dict(Counter(inventory[s]['requested_memory_gib'] for s in names)),
                    missing_evidence_memory_gib=dict(Counter(inventory[s]['requested_memory_gib'] for s in names-ready)))
    report = dict(schema_version=1, created_utc=datetime.now(timezone.utc).isoformat(),
        status='proposal_not_executable', submission_authorized=False,
        metadata_passed=not errors, errors=errors,
        sources={k: {'path': str(p), 'sha256': digest(p)} for k, p in sources.items()},
        generator_sha256=digest(__file__), full_summary=summary(reactions, closure),
        pilot_summary=summary(pilot, pilot_species),
        limitations=['Coverage is recorded publication/hash evidence, not fresh numerical/native revalidation.',
                    'Candidate scan limited to project data root; orbital path is the existing workflow candidate, not an exhaustive archive discovery.',
                    'Orbital existence/size only; full archive integrity and basis compatibility remain launch gates.',
                    'Historical resource requests are planning classes, not live scheduler validation or runtime predictions.',
                    'Stage markers are presence-only; partial stage reuse requires contract-specific validation.'],
        pilot_policy={'status': 'proposed_for_review', 'seed_reactions': seed_ids,
                      'selection': 'Retain20; one per SI row; fill by lowest selected/full property-class fraction, then incremental max memory, sum AO^3, new species count, training index.',
                      'bias': 'Cost-aware workflow pilot, not unbiased performance sample; not guaranteed to cover every memory class.',
                      'weights': 'Original Cycle2 objective weights, no renormalization.',
                      'reference_or_residual_used_for_selection': False},
        orbital_missing_count=sum(not r['orbital_candidate_exists'] for r in species_rows))
    report['metadata_checks'] = dict(input_hashes_passed=sum(r['input_hash_verified'] for r in species_rows),
        basis_bridge_identity_status_passed=sum(r['basis_bridge_identity_verified'] for r in species_rows),
        unique_training_ids=True, sequential_training_order=True,
        finite_reference_hartree=True, positive_original_weights=True,
        training_roles_and_no_final_assessment=True,
        note='Boolean checks describe the successful path; consult metadata_passed/errors for any failures.')
    args.output.mkdir(parents=True)
    for filename, value in [('audit.json', report), ('full1498_reactions.json', reactions),
                            ('species_coverage.json', species_rows), ('pilot100_reactions.json', pilot),
                            ('pilot100_species.json', [r for r in species_rows if r['species'] in pilot_species])]:
        (args.output / filename).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')
    (args.output/'checksums.json').write_text(json.dumps({p.name: digest(p) for p in sorted(args.output.glob('*.json'))}, indent=2)+'\n')
    print(json.dumps({k: report[k] for k in ('metadata_passed', 'errors', 'full_summary', 'pilot_summary', 'orbital_missing_count')}, indent=2))


if __name__ == '__main__':
    main()
