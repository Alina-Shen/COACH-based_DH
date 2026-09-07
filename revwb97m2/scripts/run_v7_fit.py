"""One explicit v7 diagnostic solve. No submission or automatic bulk scan."""
import argparse
import json
from pathlib import Path
import numpy as np
from revwb97m2.fit_spec import load_fit_settings, DEFAULT_SPEC
from revwb97m2.fit_inputs import load_inputs, digest
from revwb97m2.mio import build_model, audit_solution
from revwb97m2.grid_selection import select_rows
from revwb97m2.solver_reporting import strict_dumps, gap_report


def load_start(path, identity):
    path = Path(path)
    contract = json.loads((path/'contract.json').read_text())
    result = json.loads((path/'result.json').read_text())
    if any(contract[key] != identity[key] for key in ('specification_sha256','input_manifest_sha256')):
        raise ValueError('warm-start identity mismatch')
    if result.get('passed') is not True:
        raise ValueError('warm start has no validated incumbent')
    for name, sha in result['artifacts'].items():
        if digest(path/name) != sha:
            raise ValueError('warm-start artifact changed')
    coeff = np.load(path/'coefficients.npy', allow_pickle=False)
    selected = np.load(path/'selected.npy', allow_pickle=False)
    if coeff.shape != (292,) or selected.shape != (292,) or not np.isfinite(coeff).all():
        raise ValueError('invalid warm start')
    return coeff, selected


def readback(path, identity, arrays, settings):
    path=Path(path)
    c,z=load_start(path,identity)
    contract=json.loads((path/'contract.json').read_text())
    result=json.loads((path/'result.json').read_text())
    d=None
    if contract['grid_candidates']:
        rows=np.load(path/'grid_rows.npy',allow_pickle=False)
        candidates=np.stack([load_start(Path(p),identity)[0] for p in contract['grid_candidates']])
        expected=select_rows(arrays['grid_difference_99590'],candidates,
                             settings.candidate_rows,settings.global_rows)
        if not np.array_equal(rows,expected):
            raise ValueError('grid selection readback mismatch')
        d=arrays['grid_difference_99590'][rows]
    audit=audit_solution(arrays['feature_matrix'],arrays['target'],arrays['objective_weight'],
                         c,z,model_name='R2',budget=contract['budget'],grid_difference=d,settings=settings)
    if not audit['passed'] or not np.isclose(result['objective'],audit['regularized_objective_hartree2'],
                                            rtol=1e-7,atol=1e-10):
        raise ValueError('independent incumbent readback failed')
    return c,z


def run(args, env=None):
    settings = load_fit_settings(args.spec)
    arrays, manifest = load_inputs(args.manifest, settings)
    if args.budget not in settings.budgets:
        raise ValueError('budget not in declared scan')
    identity = {'specification_sha256':settings.specification_sha256,
                'input_manifest_sha256':digest(args.manifest)}
    out = Path(args.output)
    contract = {**identity, 'resolved_settings':settings.record(), 'budget':args.budget,
                'seconds':args.seconds if args.seconds is not None else settings.seconds,
                'threads':args.threads if args.threads is not None else settings.threads,
                'purpose':'bounded_validation_not_bulk_authorization',
                'start':None if args.start is None else str(args.start.resolve()),
                'grid_candidates':[str(p.resolve()) for p in args.grid_candidates],
                'code_sha256':{str(p):digest(p) for p in [Path(__file__),
                    Path(__file__).parents[1]/'mio.py', Path(__file__).parents[1]/'fit_spec.py',
                    Path(__file__).parents[1]/'fit_inputs.py', Path(__file__).parents[1]/'grid_selection.py',
                    Path(__file__).parents[1]/'solver_reporting.py']}}
    # JSON-normalize tuple settings before comparisons on resume.
    contract = json.loads(strict_dumps(contract))
    contract['parent_sha256'] = {str(p.resolve()):{
        name:digest(p/name) for name in ('contract.json','result.json','coefficients.npy','selected.npy')}
        for p in set(args.grid_candidates + ([args.start] if args.start else []))}
    if args.resume:
        if json.loads((out/'contract.json').read_text()) != contract:
            raise ValueError('resume contract changed')
        readback(out, identity, arrays, settings)
        return 0
    a,b,w = (arrays[key] for key in ('feature_matrix','target','objective_weight'))
    d = None
    rows = None
    if args.grid_candidates:
        candidates = np.stack([readback(p, identity, arrays, settings)[0] for p in args.grid_candidates])
        rows = select_rows(arrays['grid_difference_99590'], candidates,
                           settings.candidate_rows, settings.global_rows)
        d = arrays['grid_difference_99590'][rows]
    start = readback(args.start, identity, arrays, settings) if args.start else None
    out.mkdir(parents=True, exist_ok=False)
    (out/'contract.json').write_text(strict_dumps(contract)+'\n')
    model = None
    try:
        model,beta,z = build_model(a,b,w,budget=args.budget,grid_difference=d,
                                  settings=settings,seconds=args.seconds,threads=args.threads,env=env)
        if start is not None:
            for i in beta:
                beta[i].Start=float(start[0][i]); z[i].Start=float(start[1][i])
        model.optimize()
        result = {'passed':False, 'status':model.Status, 'solution_count':model.SolCount,
                  'runtime_seconds':model.Runtime,'artifacts':{}}
        if model.SolCount and model.Status in (2,9):
            coeff=np.array([beta[i].X for i in range(292)])
            selected=np.array([z[i].X > .5 for i in range(292)])
            audit=audit_solution(a,b,w,coeff,selected,model_name='R2',budget=args.budget,
                                 grid_difference=d,settings=settings)
            agrees=bool(np.isclose(model.ObjVal,audit['regularized_objective_hartree2'],rtol=1e-7,atol=1e-10))
            result.update(audit=audit, objective=model.ObjVal, objective_agrees=agrees,
                          bound=model.ObjBound, **gap_report(model.ObjVal,model.ObjBound,model.MIPGap))
            result['grid_max_kcal_mol']={g:float(np.max(np.abs(arrays['grid_difference_'+g]@coeff))*settings.conversion)
                                       for g in ('99590','75302')}
            result['passed']=audit['passed'] and agrees
            if result['passed']:
                np.save(out/'coefficients.npy',coeff); np.save(out/'selected.npy',selected)
                if rows is not None:
                    np.save(out/'grid_rows.npy',rows)
                result['artifacts']={p.name:digest(p) for p in out.glob('*.npy')}
        (out/'result.json').write_text(strict_dumps(result)+'\n')
        return 0 if result['passed'] else 1
    except Exception as exc:
        # Exception text can contain credential details; store only type/code.
        (out/'failure.json').write_text(strict_dumps({'error_type':type(exc).__name__,
                                                     'error_code':getattr(exc,'errno',None)})+'\n')
        return 1
    finally:
        if model is not None:
            model.dispose()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--spec',type=Path,default=DEFAULT_SPEC)
    parser.add_argument('--manifest',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--budget',type=int,required=True)
    parser.add_argument('--seconds',type=int)
    parser.add_argument('--threads',type=int)
    parser.add_argument('--start',type=Path)
    parser.add_argument('--grid-candidates',nargs='*',type=Path,default=[])
    parser.add_argument('--resume',action='store_true')
    args=parser.parse_args()
    # Require the activated dh environment's license path; no restricted fallback.
    import os
    import gurobipy as gp
    fields={}
    for line in Path(os.environ['GRB_LICENSE_FILE']).read_text().splitlines():
        key,sep,value=line.partition('=')
        if sep and key.strip() in ('WLSACCESSID','WLSSECRET','LICENSEID'):
            fields[key.strip()]=value.strip()
    with gp.Env(empty=True) as env:
        env.setParam('OutputFlag',0)
        for key in ('WLSACCESSID','WLSSECRET','LICENSEID'):
            env.setParam(key,int(fields[key]) if key=='LICENSEID' else fields[key])
        env.start()
        return run(args,env)


if __name__=='__main__':
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(strict_dumps({'error_type':type(exc).__name__,'error_code':getattr(exc,'errno',None)}))
        raise SystemExit(1)
