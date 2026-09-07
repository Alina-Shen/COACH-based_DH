"""Independent selected-row and energy-difference checks, without solving."""
import json
from pathlib import Path
import numpy as np
from revwb97m2.qchem_scalar_features import sha256

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/step15_grid_25667476'
PARENT=ROOT/'results/step15_wls_60s_25658936'


def main():
    d=np.load(OUT/'grid_difference_99590.npy')
    a=np.load(OUT/'feature_matrix.npy')
    old=[np.load(PARENT/f'full_R2_{i}_coefficients.npy') for i in range(2)]
    # Deliberately do not call the production selection helper.
    selected=set(sorted(range(len(d)),key=lambda i:(-sum(abs(float(x)) for x in d[i]),i))[:200])
    for c in old:
        errors=np.abs(d@c)
        selected.update(sorted(range(len(d)),key=lambda i:(-errors[i],i))[:100])
    checks={'independent_selection':sorted(selected)==np.load(OUT/'selected_grid_rows.npy').tolist(),
            'all_20_rows_selected':len(selected)==len(d)==20,
            'zero_grid_scalar_tail':bool(np.array_equal(d[:,-4:],np.zeros((len(d),4))))}
    rows=[]
    for repeat in range(2):
        c=np.load(OUT/f'full_R2_{repeat}_coefficients.npy')
        values={}
        for grid in ('99590','75302'):
            diff=np.load(OUT/f'grid_difference_{grid}.npy')
            direct=(a+diff)@c-a@c
            algebraic=diff@c
            checks[f'energy_difference_identity_{grid}_{repeat}']=bool(np.allclose(direct,algebraic,rtol=0,atol=1e-10))
            values[grid]={'pass1_max_kcal_mol':float(np.max(np.abs(diff@old[repeat]))*627.5094740631),
                          'pass2_max_kcal_mol':float(np.max(np.abs(algebraic))*627.5094740631)}
        checks[f'practical_grid_limit_{repeat}']=values['99590']['pass2_max_kcal_mol']<=.015+1e-9*627.5094740631
        rows.append({'repeat':repeat,'grids':values})
    report={'passed':all(checks.values()),'checks':checks,'runs':rows,
            'threshold_kcal_mol':.015,'coarse_grid_constrained':False,
            'contract_sha256':sha256(OUT/'pilot_contract.json'),
            'note':'VV10 not evaluated on both grids; frozen policy uses zero difference for it. SR-HF/PT2/D4 differences are zero. No universal grid-stability or optimality claim.'}
    with (OUT/'independent_grid_readback.json').open('x') as f:
        json.dump(report,f,indent=2,allow_nan=False)
    print(json.dumps(report,indent=2,allow_nan=False))
    return 0 if report['passed'] else 1


if __name__=='__main__':
    raise SystemExit(main())
