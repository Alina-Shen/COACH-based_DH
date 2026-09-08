"""Two-case launch adapter adopting the committed fixed-energy checkpoint."""
import argparse
import fcntl
import os
from pathlib import Path
import numpy as np
from revwb97m2.scripts import fixed_energy_checkpoint as checked

v = checked.v
CONTRACT = v.ROOT/'manifests/production_generator/large_corrected_canaries_v1.json'


def load():
    contract = v.read(CONTRACT)
    v.require(all(v.digest(p) == h for p, h in contract['hashes'].items()), 'launch source changed')
    plan, settings = v.load_plan(checked.PLAN)
    root = Path(contract['checkpoint_root'])
    report = v.read(root/'checkpoint.json')
    v.require(v.digest(root/'checkpoint.json') == contract['checkpoint_sha256'] and
              (root/'CHECKPOINT_COMPLETE').read_text().strip() == contract['checkpoint_sha256'], 'checkpoint changed')
    v.require(report['passed'] and report['original_plan_sha256'] == v.digest(checked.PLAN) and
              report['specification_sha256'] == settings.specification_sha256, 'checkpoint science mismatch')
    v.require([c['species'] for c in report['cases']] == list(v.NAMES[:5]), 'five smaller cases required')
    v.require(all(v.digest(root/p) == h for p, h in report['artifacts'].items()), 'checkpoint artifacts changed')
    for case in report['cases']:
        v.require(case['passed'] and all(v.digest(p) == h for p, h in case['dependencies'].items()), 'checkpoint evidence changed')
    out = Path(contract['output_root'])
    v.require(out.resolve().parent == v.DATA.resolve(), 'unsafe corrected output root')
    return contract, plan, settings


def require_case(plan, name, cpus, memory):
    v.require(name in v.NAMES[5:], 'only the two large canaries authorized')
    case = next(c for c in plan['cases'] if c['species'] == name)
    v.require((cpus, memory) == (case['resources']['cpus'], case['resources']['requested_memory_gib']), 'allocation mismatch')
    return case


def validate(name):
    contract, plan, settings = load()
    v.require(name in v.NAMES[5:], 'wrong species')
    case = next(c for c in plan['cases'] if c['species'] == name)
    dest = Path(contract['output_root'])/name
    record = v.read(dest/'publication.json')
    v.require(record['contract_sha256'] == v.digest(CONTRACT) and
              (dest/'LARGE_CANARY_COMPLETE').read_text().strip() == v.digest(dest/'publication.json'), 'completion changed')
    v.require(all(v.digest(dest/p) == h for p, h in record['artifacts'].items()), 'publication changed')
    report, vector, fixed, differences = checked.audit_case(plan, settings, case)
    checked.compare_vectors(np.load(dest/'feature_vector_292.npy'), vector)
    v.require(v.read(dest/'fixed_energy.json') == fixed and v.read(dest/'audit.json') == report, 'fixed/dependency readback changed')
    for g, d in differences.items():
        v.require(np.array_equal(np.load(dest/f'grid_difference_{g}.npy'), d), 'grid changed')


def run(name, cpus, memory):
    contract, plan, settings = load()
    case = require_case(plan, name, cpus, memory)
    for env, key in [('SLURM_JOB_PARTITION','partition'), ('SLURM_JOB_ACCOUNT','account'), ('SLURM_JOB_QOS','qos')]:
        v.require(os.environ.get(env) == case['route'][key], 'scheduler route mismatch')
    v.require(v.canonical_tree_hash(v.tree_manifest(Path(case['orbital_root']))) == case['source_tree_sha256'], 'source restart changed')
    v.require(min(v.available_bytes(plan['output_root']), v.available_bytes(plan['scratch_root'])) >
              plan['minimum_copy_bytes']+memory*1024**3, 'insufficient storage headroom')
    raw = Path(plan['output_root'])/name
    raw.mkdir(parents=True, exist_ok=True)
    with (raw/'corrected_launch.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        identity = dict(plan_sha256=v.digest(checked.PLAN), species=name)
        if (raw/'identity.json').exists():
            v.require(v.read(raw/'identity.json') == identity, 'stale raw root')
        else:
            v.write(raw/'identity.json', identity)
        dest = Path(contract['output_root'])/name
        if (dest/'LARGE_CANARY_COMPLETE').exists():
            validate(name)
            return
        v.require(not dest.exists(), 'partial publication preserved; review required')
        for g, derived in v.stage_inputs(Path(case['authoritative_input']).read_text(), settings, case['basis_bridge']).items():
            print(name, 'stage', g, flush=True)
            v.run_stage(raw/'stages'/g, g, derived, case, v.digest(checked.PLAN), cpus)
            if g in v.GRIDS:
                v.publish_or_resume(raw/'stages'/g, raw/'q4'/g)
        report, vector, fixed, differences = checked.audit_case(plan, settings, case)
        report2, vector2, fixed2, differences2 = checked.audit_case(plan, settings, case)
        v.require(report == report2 and fixed == fixed2, 'repeat fixed audit mismatch')
        checked.compare_vectors(vector, vector2)
        v.require(all(np.array_equal(differences[g], differences2[g]) for g in differences), 'repeat grid mismatch')
        dest.mkdir(parents=True)
        np.save(dest/'feature_vector_292.npy', vector)
        v.write(dest/'fixed_energy.json', fixed)
        v.write(dest/'audit.json', report)
        for g, d in differences.items():
            np.save(dest/f'grid_difference_{g}.npy', d)
        v.write(dest/'publication.json', dict(contract_sha256=v.digest(CONTRACT), species=name,
            original_plan_sha256=v.digest(checked.PLAN), specification_sha256=settings.specification_sha256,
            artifacts={p.name:v.digest(p) for p in dest.iterdir()}))
        (dest/'LARGE_CANARY_COMPLETE').write_text(v.digest(dest/'publication.json')+'\n')
        validate(name)
        print(name, 'corrected large canary PASS', flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=['check','run','validate'])
    p.add_argument('--species')
    p.add_argument('--cpus', type=int)
    p.add_argument('--memory-gib', type=int)
    a = p.parse_args()
    if a.action == 'check':
        load()
        print('Checkpoint, native plan/build and launch contract PASS')
    elif a.action == 'validate':
        validate(a.species)
    else:
        run(a.species, a.cpus, a.memory_gib)
