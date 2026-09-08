"""Isolated corrected-parser checkpoint; no native jobs or historical mutations."""
import argparse
import re
from pathlib import Path
import numpy as np
from revwb97m2 import v7_canary as v
from revwb97m2.qchem_scalar_features import FLOAT
from revwb97m2.scripts.recover_v7_canary_d4 import compare_vectors

PLAN = v.ROOT/'manifests/production_generator/v7_canary_v1.json'


def corrected_fixed(text, sr):
    """Prefer final energy-breakdown spelling; use full spelling only as fallback.

    Do not modify the shared multi-pattern helper or historical frozen behavior.
    """
    old = v.parse_qchem_fixed_energy_output(text, sr)
    matches = re.findall(rf'Nuclear\s+Repu\.\s+Energy\s*=\s*({FLOAT})', text, re.I)
    if not matches:
        matches = re.findall(rf'Nuclear\s+Repulsion\s+Energy\s*=\s*({FLOAT})', text, re.I)
    v.require(bool(matches), 'missing nuclear repulsion')
    nuclear = float(matches[-1].replace('D', 'E').replace('d', 'e'))
    result = dict(old, nuclear_repulsion_hartree=nuclear)
    base = nuclear + old['one_electron_hartree'] + old['coulomb_hartree']
    result['fixed_energy_hartree'] = base + old['full_long_range_hf_exchange_hartree']
    result['pure_hf_reconstruction_error_hartree'] = base + old['full_hf_exchange_hartree'] - old['pure_hf_reported_energy_hartree']
    v.require(all(np.isfinite(x) for x in result.values() if isinstance(x, float)), 'nonfinite corrected energy')
    return result


def audit_case(plan, settings, case):
    root = Path(plan['output_root'])/case['species']
    source = Path(case['authoritative_input']).read_text()
    v.require(v.digest(case['authoritative_input']) == case['input_sha256'], 'input changed')
    v.require(v.canonical_tree_hash(v.tree_manifest(Path(case['orbital_root']))) == case['source_tree_sha256'], 'source restart changed')
    v.require(v.read(root/'identity.json') == dict(plan_sha256=v.digest(PLAN), species=case['species']), 'identity changed')
    v.require(not re.search(r'(?im)^\s*\$(?:multipole_field|efield)\b', source), 'field case needs separate parser audit')
    stages = v.stage_inputs(source, settings, case['basis_bridge'])
    dependencies = {str(root/'identity.json'): v.digest(root/'identity.json')}
    for g, derived in stages.items():
        stage = root/'stages'/g
        v.validate_stage(stage, derived, case, v.digest(PLAN))
        for p in [stage/'STAGE_COMPLETE.json', *[stage/f for f in v.read(stage/'STAGE_COMPLETE.json')['artifacts']]]:
            dependencies[str(p)] = v.digest(p)
    semilocal = {}
    for g in v.GRIDS:
        checks, _ = v.validate_published_artifact(root/'q4'/g, root/'stages'/g)
        v.require(bool(checks) and all(checks.values()), 'Q4 invalid')
        p = root/'q4'/g/'semilocal_features_288.npy'
        semilocal[g] = np.load(p, allow_pickle=False)
        dependencies[str(p)] = v.digest(p)
    values = v.scalar_values((root/'stages/scalar/qchem.out').read_text(),
        (root/'stages/pt2/qchem.out').read_text() if 'pt2' in stages else None,
        one_electron=case['electron_count'] == 1)
    v.require(abs(values.get('pt2_scaled_identity_error_hartree', 0)) <= 5.2e-9, 'PT2 identity')
    text = (root/'stages/fixed/qchem.out').read_text()
    old = v.parse_qchem_fixed_energy_output(text, values['short_range_hf_hartree'])
    fixed = corrected_fixed(text, values['short_range_hf_hartree'])
    v.require(abs(fixed['pure_hf_reconstruction_error_hartree']) <= 2e-8, 'corrected HF identity failed')
    vector = np.r_[semilocal['250974'], values['short_range_hf_hartree'], values['vv10_hartree'],
                   values['pt2_total_hartree'], v.evaluate_d4_atm_from_qchem_input(source)]
    v.require(vector.shape == (292,) and np.isfinite(vector).all(), 'invalid vector')
    differences = {g: np.r_[semilocal[g]-semilocal['250974'], np.zeros(4)] for g in v.GRIDS[1:]}
    previous = (root/'species.json').is_file()
    if previous:
        record = v.read(root/'species.json')
        v.require(record['plan_sha256'] == v.digest(PLAN) and record['specification_sha256'] == settings.specification_sha256, 'stale old publication')
        for p, h in record['artifacts'].items():
            v.require(v.digest(root/p) == h, 'old publication changed')
            dependencies[str(root/p)] = h
        dependencies[str(root/'species.json')] = v.digest(root/'species.json')
        compare_vectors(np.load(root/'ready/feature_vector_292.npy'), vector)
        v.require(v.read(root/'ready/fixed_energy.json') == old, 'old fixed readback mismatch')
        v.require(v.read(root/'ready/scalar_values.json') == values, 'old scalar changed')
        for g, d in differences.items():
            v.require(np.array_equal(np.load(root/f'ready/grid_difference_{g}.npy'), d), 'old grid changed')
    report = dict(species=case['species'], passed=True, previous_publication=previous,
        old_fixed=old, corrected_fixed=fixed,
        fixed_change_hartree=fixed['fixed_energy_hartree']-old['fixed_energy_hartree'],
        dependencies=dependencies, native_stage_count=len(stages))
    return report, vector, fixed, differences


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--contract', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--verify-only', action='store_true')
    args = parser.parse_args()
    contract = v.read(args.contract)
    v.require(all(v.digest(p) == h for p, h in contract['hashes'].items()), 'checkpoint source changed')
    plan, settings = v.load_plan(PLAN)
    if args.verify_only:
        print('Checkpoint contract and historical canary code/build hashes PASS')
        return
    v.require(not args.output.exists(), 'checkpoint output exists')
    cases = [audit_case(plan, settings, c) for c in plan['cases'][:5]]
    # Reaudit independently before any publication, including repeat D4 evaluation.
    for (r, vector, fixed, diff), case in zip(cases, plan['cases'][:5]):
        r2, vector2, fixed2, diff2 = audit_case(plan, settings, case)
        v.require(r == r2 and fixed == fixed2, 'repeat fixed/dependency audit changed')
        compare_vectors(vector, vector2)
        v.require(all(np.array_equal(diff[g], diff2[g]) for g in diff), 'repeat grid changed')
    args.output.mkdir(parents=True)
    for report, vector, fixed, differences in cases:
        dest = args.output/report['species']
        dest.mkdir()
        np.save(dest/'feature_vector_292.npy', vector)
        v.write(dest/'fixed_energy.json', fixed)
        for g, d in differences.items():
            np.save(dest/f'grid_difference_{g}.npy', d)
        v.write(dest/'audit.json', report)
    files = {str(p.relative_to(args.output)): v.digest(p) for p in args.output.rglob('*') if p.is_file()}
    v.write(args.output/'checkpoint.json', dict(passed=True, purpose='corrected_parser_candidate_not_production_release',
        contract_sha256=v.digest(args.contract), specification_sha256=settings.specification_sha256,
        original_plan_sha256=v.digest(PLAN), artifacts=files,
        cases=[r for r, _, _, _ in cases]))
    v.require(all(v.digest(args.output/p) == h for p, h in files.items()), 'checkpoint serialization mismatch')
    (args.output/'CHECKPOINT_COMPLETE').write_text(v.digest(args.output/'checkpoint.json')+'\n')
    print('PASS: five species, repeated raw readback, corrected candidate artifacts; no native reruns', flush=True)


if __name__ == '__main__':
    main()
