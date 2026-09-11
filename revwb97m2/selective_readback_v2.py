"""Read-only recovery validation with tolerant recomputed floats, exact identities.

Does not change frozen v1 code, scientific feasibility limits, or run artifacts.
"""
import argparse
import math
from pathlib import Path
import numpy as np
from revwb97m2.scripts import selective_recovery_v1 as v

REPORT_RTOL = 1e-12
REPORT_ATOL = 1e-15


def compare_report(actual, saved, path='report'):
    """Compare numerical summaries, never hashes, arrays or feasibility itself."""
    if type(actual) is not type(saved):
        raise ValueError(f'{path}: type mismatch')
    if isinstance(actual, dict):
        if actual.keys() != saved.keys():
            raise ValueError(f'{path}: keys mismatch')
        for key in actual:
            compare_report(actual[key], saved[key], f'{path}.{key}')
    elif isinstance(actual, list):
        if len(actual) != len(saved):
            raise ValueError(f'{path}: length mismatch')
        for i, (x, y) in enumerate(zip(actual, saved)):
            compare_report(x, y, f'{path}[{i}]')
    elif isinstance(actual, float):
        if not (math.isfinite(actual) and math.isfinite(saved)
                and math.isclose(actual, saved, rel_tol=REPORT_RTOL, abs_tol=REPORT_ATOL)):
            raise ValueError(f'{path}: numerical mismatch')
    elif actual != saved:
        raise ValueError(f'{path}: exact value mismatch')


def audit_case(row, root, arrays, settings, entry_ids):
    c = v.c
    folder = root / row['name']
    r, model = c.read(folder / 'result.json'), c.read(folder / 'model.json')
    b, z, rows = v.inputs(row, root, arrays, settings)
    for name, expected in [('start_coefficients', b), ('start_selection', z), ('grid_rows', rows)]:
        c.require(np.array_equal(expected, np.load(folder / (name + '.npy'))), 'start/grid identity')
    compare_report(v.a.start_audit(arrays, b, z, 80, rows, settings),
                   c.read(folder / 'start_audit.json'), 'start_audit')
    c.require((model['variables'], model['constraints'], model['binaries'], model['sos']) ==
              (584, 590 + 2 * len(rows), 292, 0), 'model dimensions')
    params = model['parameters']
    c.require(params['Threads'] == 16 and params['TimeLimit'] == 600 and params['Seed'] == settings.seed
              and all(params[k] == value for k, value in settings.solver_parameters), 'parameters')
    c.require(r['name'] == row['name'] and r['budget'] == 80 and r['passed']
              and r['status'] in (2, 9) and r['solution_count'] > 0 and not r['callback_errors'], 'solve rejected')
    actual = v.policy.audit(arrays, np.load(folder / 'coefficients.npy'),
                            np.load(folder / 'selection.npy'), 80, rows, settings, entry_ids)
    # Recompute acceptance FIRST; comparison tolerances never grant feasibility.
    c.require(actual['passed'] and actual['advancement_passed'], 'candidate infeasible')
    compare_report(actual, r['audit'], 'candidate_audit')
    c.require(np.isclose(r['objective'], actual['audit']['independent']['regularized_objective_hartree2'],
                         rtol=1e-7, atol=1e-10), 'objective mismatch')
    gaps = c.d.gap_report(r['objective'], r['bound']['value'], r['gaps']['gap'])
    c.require(gaps['gap_consistent'], 'gap mismatch')
    compare_report(gaps, r['gaps'], 'gaps')
    return dict(name=row['name'], passed=True, selected_rows=rows.tolist(), report=actual, gaps=gaps)


def validate(root):
    root = Path(root)
    c = v.c
    before = {str(f.relative_to(root)): c.digest(f) for f in root.rglob('*') if f.is_file()}
    identity = c.read(root / 'identity.json')
    p, r = v.check(Path(identity['release']))
    c.require(identity['plan_sha256'] == c.digest(v.PLAN)
              and identity['release_sha256'] == c.digest(identity['release'])
              and identity['commit'] == r['commit'], 'identity')
    done, pub = c.read(root / 'completion.json'), c.read(root / 'publication.json')
    c.require(done['publication_sha256'] == c.digest(root / 'publication.json')
              and done['bulk_authorized'] is False and done['final_model_user_review_required'] is True,
              'completion identity')
    c.require(all(c.digest(root / name) == sha for name, sha in pub['artifacts'].items()), 'artifact hashes')
    settings = v.policy.settings()
    arrays, manifest = c.d.full.load_inputs(c.d.full.matrix_manifest(), settings)
    for name, (b, z) in v.source(p, arrays, settings).items():
        c.require(np.array_equal(b, np.load(root / name / 'coefficients.npy'))
                  and np.array_equal(z, np.load(root / name / 'selection.npy')), 'source copy changed')
    results = [audit_case(row, root, arrays, settings, manifest['reaction_ids']) for row in v.schedule()]
    for result in results:
        compare_report(result, c.read(root / (result['name'] + '_audit.json')), 'saved_audit')
    c.require(before == {str(f.relative_to(root)): c.digest(f) for f in root.rglob('*') if f.is_file()},
              'artifacts changed during readback')
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    args = parser.parse_args()
    for result in validate(args.root):
        print('PASS', result['name'], 'unselected-grid reporting retained; user review required')
