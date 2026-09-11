"""Read frozen v1 artifacts without changing their producer or acceptance gates."""
import argparse
from pathlib import Path
import numpy as np
from revwb97m2.scripts import continuous_k14_v1 as c


def audits_match(saved, actual):
    """Only recomputed objective scalars permit roundoff; all other fields exact."""
    if saved.keys() != actual.keys():
        return False
    numeric = {'weighted_sse', 'ridge', 'objective'}
    for key in saved:
        if key in numeric:
            if (type(saved[key]) not in (float, int) or
                    type(actual[key]) not in (float, int) or
                    not np.isfinite([saved[key], actual[key]]).all() or
                    not np.isclose(saved[key], actual[key], rtol=1e-12, atol=1e-15)):
                return False
        elif saved[key] != actual[key]:
            return False
    return True


def validate(root):
    identity=c.read(root/'identity.json')
    c.require(identity['plan_sha256']==c.digest(c.PLAN) and
              c.digest(identity['release_path'])==identity['release_sha256'], 'identity changed')
    c.check_release(identity['release_path'])
    c.require((root/'CONTINUOUS_DIAGNOSTIC_COMPLETE').read_text().strip()==
              c.digest(root/'publication.json'), 'incomplete diagnostics')
    pub=c.read(root/'publication.json')
    required={'identity.json'}
    for kind in c.KINDS:
        required.update(f'{kind}/{name}' for name in ('result.json','model.json','model.mps.gz','progress.jsonl'))
        if c.read(root/kind/'result.json')['solution_count']:
            required.update(f'{kind}/{name}.npy' for name in ('coefficients','selection_relaxed','residuals'))
    c.require(required <= pub['artifacts'].keys(), 'missing artifact hashes')
    c.require(all(c.digest(root/p)==h for p,h in pub['artifacts'].items()), 'artifact changed')
    settings=c.d.full.load_fit_settings()
    arrays,_=c.d.full.load_inputs(c.d.full.matrix_manifest(),settings)
    results=[]
    for kind in c.KINDS:
        folder=root/kind; result=c.read(folder/'result.json'); model=c.read(folder/'model.json')
        c.require(model['kind']==result['kind']==kind and
                  tuple(model[k] for k in ('variables','constraints','binaries','integers'))==
                  (2082,2088,0,0), 'wrong model')
        params=model['parameters']
        c.require(params['Threads']==16 and params['TimeLimit']==600 and params['Seed']==settings.seed and
                  all(params[k]==v for k,v in settings.solver_parameters), 'parameter mismatch')
        c.require(result['optimal_status']==(result['status']==2), 'incorrect optimal flag')
        if result['solution_count']:
            values=[np.load(folder/(key+'.npy'),allow_pickle=False)
                    for key in ('coefficients','selection_relaxed','residuals')]
            checked=c.audit(arrays,*values,settings,kind)
            c.require(audits_match(result['audit'],checked), 'solution audit changed')
            expected=bool(not result['callback_errors'] and result['status'] in (2,9) and
                          checked['passed'] and np.isclose(result['objective'],checked['objective'],rtol=1e-7,atol=1e-10))
            c.require(result['passed']==expected, 'wrong acceptance')
        else:
            c.require(not result['passed'] and result['objective'] is None, 'fabricated solution')
        results.append(result)
    return results,arrays,settings


def fixed_start(arrays,settings,coef,z,residual):
    """No clipping/rounding: reject fractional support and independently audit MIO."""
    c.require(np.array_equal(z, np.r_[np.zeros(288),np.ones(4)]), 'not exact fixed support')
    c.require(c.audit(arrays,coef,z,residual,settings,'fixed_scalars')['passed'], 'continuous audit failed')
    selected=z.astype(bool)
    checked=c.d.audit_solution(arrays['feature_matrix'],arrays['target'],arrays['objective_weight'],
                               coef,selected,model_name='R2',budget=14,settings=settings)
    c.require(checked['passed'], 'MIO start audit failed')
    fresh=np.sqrt(arrays['objective_weight'])*(arrays['feature_matrix']@coef-arrays['target'])
    return dict(coefficients=coef.tolist(),selected=selected.tolist(),residuals=fresh.tolist(),
                audit=checked,budget=14,grid_constraints_audited=False,submission_authorized=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    c.require(not args.output.exists(), 'preserve prior readback')
    results,arrays,settings=validate(args.root)
    c.require(results[0]['kind']=='fixed_scalars' and results[0]['passed'], 'fixed solution rejected')
    folder=args.root/'fixed_scalars'
    values=[np.load(folder/(key+'.npy'),allow_pickle=False)
            for key in ('coefficients','selection_relaxed','residuals')]
    start=fixed_start(arrays,settings,*values)
    c.write(args.output,dict(schema_version=2,source=str(args.root.resolve()),
        publication_sha256=c.digest(args.root/'publication.json'),reader_sha256=c.digest(__file__),
        matrix_sha256=c.d.full.MATRIX_SHA,input_sha256=c.d.full.INPUT_SHA,
        diagnostic_acceptance={r['kind']:r['passed'] for r in results},
        fixed_start=start,all_diagnostics_passed=all(r['passed'] for r in results)))
    print('Readback complete; acceptance:',{r['kind']:r['passed'] for r in results})


if __name__=='__main__':
    main()
