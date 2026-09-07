"""Read back pilot artifacts and audit the frozen contract and incumbents."""
import argparse
import json
from pathlib import Path
import numpy as np
from revwb97m2.mio import audit_solution
from revwb97m2.qchem_scalar_features import sha256
from revwb97m2.solver_reporting import gap_report,raw_gap_from_record,strict_dumps
from revwb97m2.grid_selection import select_rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--seconds', type=int, choices=(2,60), default=2)
    parser.add_argument('--full-only', action='store_true')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    out = args.output
    contract = json.loads((out/'pilot_contract.json').read_text())
    previous = json.loads((root/'results/step15_pilot_v2/pilot_contract.json').read_text())
    results = json.loads((out/'pilot_results.json').read_text())
    source = root/'manifests/reaction_features/step14_recovery_complete_v2.json'
    validation = json.loads(source.read_text())
    labels = ('full_R2',) if args.full_only else ('full_R2','reduced_support_diagnostic')
    checks = {
        'frozen_contract': all(contract[k] == v for k,v in previous.items() if k not in ('code_sha256','seconds_per_solve')),
        'requested_time_and_cases': contract['seconds_per_solve'] == args.seconds and contract.get('full_only',False) == args.full_only,
        'code_hashes': all(sha256(Path(p)) == h for p,h in contract['code_sha256'].items()),
        'source_hash': sha256(source) == contract['source_validation_sha256'],
        'input_hashes': all(sha256(out/p) == h for p,h in validation['artifacts_sha256'].items() if p.endswith('.npy')),
        'expected_runs': [(r['label'],r['repeat']) for r in results['outcomes']] ==
            [(label,i) for label in labels for i in range(2)],
    }
    a = np.load(out/'feature_matrix.npy')
    b = np.load(out/'target.npy')
    w = np.load(out/'objective_weight.npy')
    grid_difference=None
    if 'grid_pass2' in contract:
        g=contract['grid_pass2']
        checks['grid_parent_hashes']=all(sha256(Path(p))==h for p,h in g['parent_hashes'].items())
        checks['grid_selection_hashes']=all(sha256(out/p)==h for p,h in g['selection_hashes'].items())
        parent=Path(g['parent'])
        starts=np.stack([np.load(parent/f'full_R2_{i}_coefficients.npy') for i in range(2)])
        rows=select_rows(np.load(out/'grid_difference_99590.npy'),starts)
        grid_difference=np.load(out/'selected_grid_difference.npy')
        checks['grid_selection_rebuilt']=np.array_equal(rows,np.load(out/'selected_grid_rows.npy')) and np.array_equal(grid_difference,np.load(out/'grid_difference_99590.npy')[rows])
    summaries = []
    for r in results['outcomes']:
        label, repeat = r['label'], r['repeat']
        coeff = np.load(out/f'{label}_{repeat}_coefficients.npy')
        selected = np.load(out/f'{label}_{repeat}_selected.npy')
        budget = 14 if label == 'full_R2' else 7
        audit = audit_solution(a,b,w,coeff,selected,model_name='R2',budget=budget,grid_difference=grid_difference)
        agrees = bool(np.isclose(r['objective'],audit['weighted_sse_hartree2'],rtol=1e-7,atol=1e-10))
        checks[f'{label}_{repeat}'] = audit['passed'] and agrees and r['solution_count'] > 0 and 'gurobi_error' not in r
        summaries.append({'label':label,'repeat':repeat,'status':r['status'],
                          'support_count':int(selected.sum()),'objective':r['objective'],
                          **gap_report(r['objective'],r['bound'],raw_gap_from_record(r)),
                          'bound':r['bound'],'audit':audit})
    repeat_differences = {}
    for label in labels:
        c0 = np.load(out/f'{label}_0_coefficients.npy')
        c1 = np.load(out/f'{label}_1_coefficients.npy')
        repeat_differences[label] = float(np.max(np.abs(c0-c1)))
    report = {'passed':all(checks.values()),'checks':checks,'runs':summaries,
              'repeat_max_coefficient_difference':repeat_differences,
              'interpretation':'bounded engineering validation, not convergence or coefficient selection'}
    with (out/'readback_audit.json').open('x') as handle:
        handle.write(strict_dumps(report))
        handle.write('\n')
    print(strict_dumps(report))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
