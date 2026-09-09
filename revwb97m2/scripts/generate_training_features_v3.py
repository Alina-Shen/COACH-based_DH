"""Version3 full-training generation with explicit compatibility and exact21-ECP scope.

Lives outside the top-level package glob pinned by active canaries. Native stage
implementation is reused unchanged. No monkey-patching of the canary contract.
"""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path

import numpy as np
from revwb97m2 import v7_canary as native
from revwb97m2.scripts import corrected_canary_evidence_v2 as corrected
from revwb97m2.scripts import generation_compat_v1 as compat, ecp21_inputs_v1 as ecp
from revwb97m2.scripts.recover_v7_canary_d4 import compare_vectors, audit as audit_canary

ROOT = native.ROOT
PILOT = ROOT/'results/training_preflight_v2/pilot100_species.json'
CANARY = ROOT/'manifests/production_generator/v7_canary_v1.json'
SCRIPT = Path(__file__).resolve()
LAUNCHER = ROOT/'slurm/run_training_features_v2.sh'
ARRAY_LAUNCHER = ROOT/'slurm/run_full_training_features_v3.sh'
APPROVED_ROUTES = {('mhg', 'mhg', 'normal'), ('cm1', 'lr_qchem', 'condo_qchem'),
                   ('lr8', 'lr_mhg2', 'mhg2_lr8_normal'),
                   ('lr7', 'lr_mhg2', 'condo_mhg_lr7')}


def hashes():
    return dict(compat.native_dependencies(), **{str(p): native.digest(p) for p in
        (SCRIPT, ROOT/'scripts/recover_v7_canary_d4.py', LAUNCHER, ARRAY_LAUNCHER,
         ROOT/'scripts/corrected_canary_evidence.py', ROOT/'scripts/fixed_energy_checkpoint.py',
         ROOT/'scripts/run_large_corrected_canaries.py', corrected.REGISTRY,
         Path(corrected.__file__), Path(compat.__file__), Path(ecp.__file__), compat.CONTRACT, ecp.REVIEW)})


def choose_first(rows, count=16):
    candidates = [r for r in rows if r['coverage'] == 'no_feature_candidates' and
                  int(r['requested_memory_gib']) == 14]
    selected = sorted(candidates, key=lambda r: (int(r['orbital_aos']), r['species']))[:count]
    native.require(len(selected) == count and count > 0, 'insufficient first-tranche candidates')
    return selected


def safe_name(name):
    native.require(name not in ('', '.', '..') and Path(name).name == name,
                   'unsafe species name')


def validate_reuse(ref, name):
    """v2 only accepts the explicitly corrected registry; no silent legacy migration."""
    native.require(ref['kind'] == 'corrected', 'legacy reuse needs explicit corrected migration')
    native.require(Path(ref['plan']).resolve() == corrected.REGISTRY.resolve() and
                   native.digest(ref['plan']) == ref['plan_sha256'], 'wrong/stale evidence registry')
    return corrected.validate_registry()[name]


def freeze(path, names, namespace):
    settings = native.load_fit_settings()
    safe_name(namespace)
    rows = {r['species']: r for r in csv.DictReader(native.INVENTORY.open())}
    bridges = {r['species']: r for r in csv.DictReader(native.BRIDGE.open())}
    native.require(names and len(names) == len(set(names)), 'empty/duplicate species selection')
    out = native.DATA/namespace
    scratch = native.SCRATCH/namespace
    native.require(not out.exists() and not scratch.exists(), 'namespace already exists')
    cases = []
    for name in names:
        safe_name(name)
        row, bridge = rows[name], bridges[name]
        source = Path(row['qchem_input_path'])
        native.require(native.digest(source) == row['qchem_input_sha256'], 'source input changed')
        native.require(bridge['qchem_source_input_sha256'] == row['qchem_input_sha256'] and
                       bridge['source_record_sha256'] == row['source_record_sha256'] and
                       bridge['runnable_status'] == 'runnable_basis_metadata_validated', 'bridge changed')
        native.require(int(row['ghost_atom_count']) == 0, 'unsupported ghost centers')
        count, spin = ecp.electron_count(source.read_text(), bridge)
        native.require((count, spin) == (int(row['electron_count']), int(row['spin'])), 'inventory electron/spin mismatch')
        inputs = ecp.stage_inputs(source.read_text(), settings, bridge)
        orbital = native.ORBITALS/name
        tree = native.tree_manifest(orbital)
        native.require(tree and (orbital/'qarchive.h5').is_file(), 'missing restart tree')
        native.require(any(r['bytes'] > 800 for r in tree), 'restart tree contains no substantial files')
        cases.append(dict(species=name, authoritative_input=str(source), input_sha256=native.digest(source),
            orbital_root=str(orbital), source_tree=tree,
            source_tree_sha256=native.canonical_tree_hash(tree),
            source_tree_bytes=sum(r['bytes'] for r in tree), qarchive_sha256=native.digest(orbital/'qarchive.h5'),
            source_record_sha256=row['source_record_sha256'], electron_count=count, spin=spin,
            basis_bridge=bridge, scratch_root=str(scratch/name),
            resources={k: int(row[k]) for k in ('cpus', 'requested_memory_gib', 'wall_hours')},
            route={k: row[k] for k in ('partition', 'account', 'qos')},
            stages={g: {'action': 'generate_or_resume_same_contract', 'input': text,
                        'input_sha256': hashlib.sha256(text.encode()).hexdigest()} for g, text in inputs.items()},
            pt2_policy='one_electron_zero' if count == 1 else 'native_total_pt2',
            cross_campaign_partial_reuse='not_authorized_without_explicit_raw_stage_validation'))
    build = native.read(CANARY)['build_hashes']
    native.require(all(native.digest(p) == h for p, h in build.items()), 'build changed')
    native.write(path, dict(schema_version=2, purpose='generic_training_feature_batch_corrected',
        corrected_evidence_sha256=native.digest(corrected.REGISTRY),
        submission_authorized=False, all_seven_canaries_required=True, user_commit_required=True,
        output_root=str(out), scratch_root=str(scratch), cases=cases,
        inventory_sha256=native.digest(native.INVENTORY), basis_bridge_sha256=native.digest(native.BRIDGE),
        specification_sha256=settings.specification_sha256, code_hashes=hashes(), build_hashes=build,
        selection_source={'path': str(ROOT/'results/training_preflight_v2/full1498_reactions.json'),
                          'sha256': native.digest(ROOT/'results/training_preflight_v2/full1498_reactions.json')},
        concurrency_proposal=None, resource_review_pending=True,
        minimum_copy_bytes=sum(c['source_tree_bytes']*len(c['stages']) for c in cases),
        storage_free_bytes_at_freeze=min(native.available_bytes(out), native.available_bytes(scratch)),
        storage_note='Copies lower bound only; new native scratch/logs need extra headroom. No reservation.',
        stage_reuse_policy='Only completed stages under identical plan/input/source hashes; partial stages stop.',
        full_reuse_policy='Explicit refresh/canary readback via audit-reuse; never infer readiness from files.'))
    return native.read(path)


def load(path):
    plan = native.read(path)
    native.require(plan['schema_version'] == 2 and plan['purpose'] == 'generic_training_feature_batch_corrected', 'wrong plan')
    settings = native.load_fit_settings()
    native.require(plan['corrected_evidence_sha256'] == native.digest(corrected.REGISTRY), 'evidence registry changed')
    native.require(plan['specification_sha256'] == settings.specification_sha256, 'spec changed')
    native.require(plan['inventory_sha256'] == native.digest(native.INVENTORY) and
                   plan['basis_bridge_sha256'] == native.digest(native.BRIDGE), 'inventory/bridge changed')
    native.require(plan['code_hashes'] == hashes(), 'code changed')
    native.require(all(native.digest(p) == h for p, h in plan['build_hashes'].items()), 'build changed')
    out, scratch = Path(plan['output_root']), Path(plan['scratch_root'])
    native.require(out.resolve().parent == native.DATA.resolve() and
                   scratch.resolve() == (native.SCRATCH/out.name).resolve(), 'unsafe namespace')
    native.require(len({c['species'] for c in plan['cases']}) == len(plan['cases']), 'duplicate species')
    for c in plan['cases']:
        safe_name(c['species'])
        native.require(Path(c['scratch_root']).resolve() == (scratch/c['species']).resolve(), 'unsafe case scratch')
        native.require(native.digest(c['authoritative_input']) == c['input_sha256'], 'source changed')
        expected = ecp.stage_inputs(Path(c['authoritative_input']).read_text(), settings, c['basis_bridge'])
        native.require(expected == {g: v['input'] for g, v in c['stages'].items()}, 'derived inputs changed')
    return plan, settings


def reviewed_routes(plan, release):
    """Execution routing may change, never scientific inputs or memory/CPU requests."""
    routes = release.get('scheduler_routes', {c['species']: c['route'] for c in plan['cases']})
    native.require(isinstance(routes, dict) and set(routes) == {c['species'] for c in plan['cases']},
                   'release routes must cover exactly the frozen species')
    for route in routes.values():
        native.require(isinstance(route, dict) and set(route) == {'partition', 'account', 'qos'},
                       'only partition/account/qos may be overridden')
        native.require(tuple(route[k] for k in ('partition', 'account', 'qos')) in APPROVED_ROUTES,
                       'unapproved or low-priority scheduler route')
    return routes


def release_check(plan_path, release_path):
    """Require a separately reviewed release; freeze alone can never launch."""
    native.require(release_path is not None, 'release absent: wait for seven canaries, commit and resource review')
    r = native.read(release_path)
    native.require(r['plan_sha256'] == native.digest(plan_path) and r['user_approved_submission'] is True
                   and r['resource_review_passed'] is True, 'release not approved for this plan')
    native.require(r['corrected_evidence_sha256'] == native.digest(corrected.REGISTRY), 'wrong release evidence')
    corrected.validate_registry()
    # Commit must contain precisely the frozen code and plan, not merely exist.
    import subprocess
    plan = native.read(plan_path)
    reviewed_routes(plan, r)
    for p, h in dict(plan['code_hashes'], **{str(Path(plan_path).resolve()): native.digest(plan_path)}).items():
        try:
            relative = str(Path(p).relative_to(ROOT.parent))
        except ValueError:
            continue  # External control/build authorities remain hash-checked by load.
        data = subprocess.check_output(['git', 'show', r['commit']+':'+relative], cwd=ROOT.parent)
        native.require(hashlib.sha256(data).hexdigest() == h, 'uncommitted frozen code/plan')
    if any(c['basis_bridge']['ecp_resolution']=='embedded_qchem_block' for c in plan['cases']):
        native.require(r.get('ecp_native_gateway_authorized') is True,
                       'embedded-ECP native gateway requires explicit release authorization')
    return r


def validate(plan_path, name, require_marker=True):
    plan, settings = load(plan_path)
    case = next(c for c in plan['cases'] if c['species'] == name)
    root = Path(plan['output_root'])/name
    native.require(native.canonical_tree_hash(native.tree_manifest(Path(case['orbital_root']))) ==
                   case['source_tree_sha256'], 'source restart changed')
    native.require(native.read(root/'identity.json') == dict(plan_sha256=native.digest(plan_path), species=name), 'identity changed')
    native.require(not require_marker or (root/'GENERATION_COMPLETE').is_file(), 'incomplete publication')
    record = native.read(root/'species.json')
    native.require(record['plan_sha256'] == native.digest(plan_path) and
                   record['specification_sha256'] == settings.specification_sha256, 'publication identity changed')
    native.require(all(native.digest(root/p) == h for p, h in record['artifacts'].items()), 'publication hash changed')
    vector, fixed, differences, values = corrected.components(root, case, settings)
    compare_vectors(np.load(root/'ready/feature_vector_292.npy', allow_pickle=False), vector)
    native.require(native.read(root/'ready/fixed_energy.json') == fixed and
                   native.read(root/'ready/scalar_values.json') == values, 'fixed/scalar changed')
    for g, d in differences.items():
        native.require(np.array_equal(np.load(root/f'ready/grid_difference_{g}.npy'), d), 'grid changed')
    return vector, fixed, differences


def run(path, name, release, cpus, memory_gib):
    plan, settings = load(path)
    approved_release = release_check(path, release)  # Before any filesystem mutation or native calculation.
    case = next(c for c in plan['cases'] if c['species'] == name)
    native.require((cpus, memory_gib) == (case['resources']['cpus'], case['resources']['requested_memory_gib']), 'allocation mismatch')
    route = reviewed_routes(plan, approved_release)[name]
    for env, key in [('SLURM_JOB_PARTITION', 'partition'), ('SLURM_JOB_ACCOUNT', 'account'), ('SLURM_JOB_QOS', 'qos')]:
        native.require(os.environ.get(env) == route[key], 'scheduler route mismatch '+env)
    native.require(native.canonical_tree_hash(native.tree_manifest(Path(case['orbital_root']))) == case['source_tree_sha256'], 'restart tree changed')
    native.require(min(native.available_bytes(plan['output_root']), native.available_bytes(plan['scratch_root'])) >
                   plan['minimum_copy_bytes']+memory_gib*1024**3, 'insufficient storage headroom')
    root = Path(plan['output_root'])/name
    root.mkdir(parents=True, exist_ok=True)
    # Kernel lock prevents duplicate execution without deleting any lock/evidence file.
    import fcntl
    with (root/'execution.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        identity = dict(plan_sha256=native.digest(path), species=name)
        if (root/'identity.json').exists():
            native.require(native.read(root/'identity.json') == identity, 'stale root')
        else:
            native.write(root/'identity.json', identity)
        if (root/'GENERATION_COMPLETE').exists():
            validate(path, name)
            return
        for g, stage in case['stages'].items():
            native.run_stage(root/'stages'/g, g, stage['input'], case, native.digest(path), cpus)
            if g in native.GRIDS:
                native.publish_or_resume(root/'stages'/g, root/'q4'/g)
        if not (root/'species.json').exists():
            vector, fixed, differences, values = corrected.components(root, case, settings)
            ready = root/'ready'
            native.require(not ready.exists(), 'partial ready publication: preserve and review')
            ready.mkdir()
            np.save(ready/'feature_vector_292.npy', vector)
            for g, d in differences.items():
                np.save(ready/f'grid_difference_{g}.npy', d)
            native.write(ready/'fixed_energy.json', fixed)
            native.write(ready/'scalar_values.json', values)
            native.write(root/'species.json', dict(plan_sha256=native.digest(path),
                specification_sha256=settings.specification_sha256, species=name,
                d4_readback_absolute_tolerance_hartree=1e-12,
                artifacts={str(p.relative_to(root)): native.digest(p) for p in ready.iterdir()}))
        validate(path, name, require_marker=False)
        (root/'GENERATION_COMPLETE').write_text('complete\n')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=['freeze-first', 'check', 'run', 'validate', 'audit-reuse', 'check-evidence'])
    p.add_argument('--plan', type=Path, required=True)
    p.add_argument('--namespace', default='training_first16_v2')
    selection = p.add_mutually_exclusive_group()
    selection.add_argument('--species')
    selection.add_argument('--species-index', type=int)
    p.add_argument('--release', type=Path)
    p.add_argument('--reuse-kind', choices=['canary', 'refresh', 'corrected'])
    p.add_argument('--recovery')
    p.add_argument('--cpus', type=int)
    p.add_argument('--memory-gib', type=int)
    a = p.parse_args()
    if a.species_index is not None:
        cases = native.read(a.plan)['cases']
        native.require(0 <= a.species_index < len(cases), 'species index out of range')
        a.species = cases[a.species_index]['species']
    if a.action == 'freeze-first':
        result = freeze(a.plan, [r['species'] for r in choose_first(native.read(PILOT))], a.namespace)
        print(json.dumps({'species': [c['species'] for c in result['cases']], 'minimum_copy_bytes': result['minimum_copy_bytes'], 'submission_authorized': False}, indent=2))
    elif a.action == 'check':
        load(a.plan)
        print('Frozen code/build/input/spec checks PASS; NOT launch approval')
    elif a.action == 'check-evidence':
        evidence = corrected.validate_registry()
        print('PASS: corrected seven-species evidence', sorted(evidence))
    elif a.action == 'run':
        run(a.plan, a.species, a.release, a.cpus, a.memory_gib)
    elif a.action == 'validate':
        validate(a.plan, a.species)
    else:
        validate_reuse(dict(kind=a.reuse_kind, plan=str(a.plan), plan_sha256=native.digest(a.plan), recovery=a.recovery), a.species)
        print('Independent completed-source reuse audit PASS; no data changed')


if __name__ == '__main__':
    main()
