"""Versioned D4-only readback recovery; never modify frozen canary code/data."""
import argparse
from pathlib import Path
import numpy as np
from revwb97m2 import v7_canary as original
from revwb97m2.fit_inputs import digest

D4_TOLERANCE_HARTREE = 1e-12


def compare_vectors(stored, regenerated):
    original.require(stored.shape == regenerated.shape == (292,), 'invalid vector shape')
    original.require(np.isfinite(stored).all() and np.isfinite(regenerated).all(), 'nonfinite vector')
    original.require(np.array_equal(stored[:291], regenerated[:291]), 'non-D4 feature changed')
    delta = float(regenerated[291]-stored[291])
    original.require(abs(delta) <= D4_TOLERANCE_HARTREE, 'D4 change exceeds approved tolerance')
    return delta


def audit(plan_path, species):
    plan, settings = original.load_plan(plan_path)
    case = next(c for c in plan['cases'] if c['species'] == species)
    root = Path(plan['output_root'])/species
    original.require(digest(case['authoritative_input']) == case['input_sha256'], 'source input changed')
    original.require(original.read(root/'identity.json') ==
                     dict(plan_sha256=digest(plan_path), species=species), 'species identity changed')
    record = original.read(root/'species.json')
    original.require(record['plan_sha256'] == digest(plan_path) and
                     record['specification_sha256'] == settings.specification_sha256, 'stale publication')
    original.require(all(digest(root/p) == h for p, h in record['artifacts'].items()),
                     'published artifact hash changed')
    # Rechecks each native stage, Q4 artifact, scalar/PT2/fixed parser and scratch.
    vector, fixed, differences, values = original.components(root, case, settings)
    stored = np.load(root/'ready/feature_vector_292.npy', allow_pickle=False)
    delta = compare_vectors(stored, vector)
    original.require(original.read(root/'ready/fixed_energy.json') == fixed, 'fixed readback changed')
    original.require(original.read(root/'ready/scalar_values.json') == values, 'scalar readback changed')
    for g, d in differences.items():
        original.require(np.array_equal(np.load(root/f'ready/grid_difference_{g}.npy'), d),
                         'grid readback changed')
    dependencies = [root/'identity.json', root/'species.json',
                    *[root/p for p in record['artifacts']],
                    *sorted((root/'stages').glob('*/STAGE_COMPLETE.json'))]
    return dict(schema_version=1, passed=True, species=species,
                purpose='D4_only_recovery_not_a_new_calculation',
                plan_sha256=digest(plan_path), specification_sha256=settings.specification_sha256,
                recovery_code_sha256=digest(Path(__file__)),
                d4_tolerance_hartree=D4_TOLERANCE_HARTREE,
                d4_difference_hartree=delta, stored_d4_hartree=float(stored[291]),
                original_completion_marker_present=(root/'CANARY_COMPLETE').is_file(),
                artifacts={str(p.resolve()): digest(p) for p in dependencies},
                checks=dict(original_plan_and_code=True, native_and_q4_readback=True,
                            published_hashes=True, other_291_columns_exact=True,
                            fixed_scalars_grids_exact=True, d4_within_tolerance=True))


def recover(plan_path, species, output):
    report = audit(plan_path, species)
    output = Path(output)
    if output.exists():
        saved = original.read(output/'recovery.json')
        original.require((output/'RECOVERY_COMPLETE').read_text().strip() == digest(output/'recovery.json'),
                         'recovery marker/hash mismatch')
        for key in ('schema_version', 'passed', 'species', 'plan_sha256',
                    'specification_sha256', 'recovery_code_sha256',
                    'd4_tolerance_hartree', 'artifacts', 'checks'):
            original.require(saved[key] == report[key], 'stale recovery '+key)
        return report  # Numeric D4 recomputation can differ again by one ULP.
    output.mkdir(parents=True, exist_ok=False)
    original.write(output/'recovery.json', report)
    # Fresh readback of the report before recording recovery completion.
    original.require(original.read(output/'recovery.json') == report, 'recovery serialization changed')
    (output/'RECOVERY_COMPLETE').write_text(digest(output/'recovery.json')+'\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--species', choices=original.NAMES, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = recover(args.plan, args.species, args.output)
    print(args.species, 'recovery/readback PASS; D4 delta Ha', result['d4_difference_hartree'])


if __name__ == '__main__':
    main()
