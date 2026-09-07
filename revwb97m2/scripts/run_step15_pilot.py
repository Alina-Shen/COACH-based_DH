"""Prepare named optimizer inputs and run bounded C0 solver diagnostics."""
import json
import argparse
import os
from pathlib import Path
import numpy as np
import gurobipy as gp
from revwb97m2.qchem_scalar_features import sha256
from revwb97m2.mio import feature_names,build_model,audit_solution
from revwb97m2.solver_reporting import gap_report,strict_dumps
from revwb97m2.grid_selection import select_rows

ROOT=Path(__file__).resolve().parents[1]
OUTPUT=ROOT/'results/step15_pilot_v2'


def main(output=OUTPUT, env=None, seconds=2, full_only=False, grid_pass2=None):
    OUTPUT=Path(output)
    source=ROOT/'manifests/reaction_features/step14_recovery_complete_v2.json'
    validation=json.loads(source.read_text())
    data=Path(validation['output_root'])
    assert validation['status']=='passed' and validation['reaction_count']==20
    assert all(sha256(data/file)==digest for file,digest in validation['artifacts_sha256'].items())
    OUTPUT.mkdir(exist_ok=False)
    a=np.load(data/'feature_matrix.npy'); b=np.load(data/'target.npy'); w=np.load(data/'objective_weight.npy')
    for filename in validation['artifacts_sha256']:
        if filename.endswith('.npy'):
            np.save(OUTPUT/filename,np.load(data/filename))
    names=feature_names('R2')
    schema={'R2':{'status':'available','feature_count':292,'names':names},
            'R1':{'status':'pending_same_density_features','feature_count':79,'names':feature_names('R1'),
                  'reason':'R1 same-spin gamma=0.2 differs from R2 gamma=0.01; slicing is invalid'}}
    (OUTPUT/'named_models.json').write_text(json.dumps(schema,indent=2)+'\n')
    contract={'status':'frozen_before_pilot_results','source_validation_sha256':sha256(source),
              'code_sha256':{str(p):sha256(p) for p in [ROOT/'mio.py',ROOT/'solver_reporting.py',ROOT/'grid_selection.py',Path(__file__)]},
              'profile':'C0_minimal_critical','full_R2_budget':14,'seconds_per_solve':seconds,'threads':1,'seed':0,
              'repeats':2,'purpose':'engineering_smoke_not_coefficient_selection',
              'restricted_license_diagnostic_columns':[0,8,96,104,192,200,288,289,290,291],
              'restricted_license_diagnostic_budget':7,'bulk_submission_authorized':False,
              'feature_matrix_sha256':sha256(OUTPUT/'feature_matrix.npy')}
    contract['full_only']=full_only
    grid_difference=None
    starts=None
    start_selections=None
    if grid_pass2 is not None:
        if not full_only:
            raise ValueError('grid diagnostic requires full-only')
        parent=Path(grid_pass2)
        parent_contract=json.loads((parent/'pilot_contract.json').read_text())
        if parent_contract['feature_matrix_sha256']!=contract['feature_matrix_sha256']:
            raise ValueError('pass1/pass2 feature identity mismatch')
        parent_results=json.loads((parent/'pilot_results.json').read_text())
        if not all(r.get('audit',{}).get('passed') for r in parent_results['outcomes']):
            raise ValueError('pass1 incumbents not audited')
        starts=np.stack([np.load(parent/f'full_R2_{i}_coefficients.npy') for i in range(2)])
        start_selections=np.stack([np.load(parent/f'full_R2_{i}_selected.npy') for i in range(2)])
        d=np.load(OUTPUT/'grid_difference_99590.npy')
        rows=select_rows(d,starts)
        grid_difference=d[rows]
        np.save(OUTPUT/'selected_grid_rows.npy',rows)
        np.save(OUTPUT/'selected_grid_difference.npy',grid_difference)
        contract['grid_pass2']={'parent':str(parent),'threshold_kcal_mol':0.015,
            'selected_count':len(rows),'candidate_top':100,'global_l1_top':200,
            'parent_hashes':{str(p):sha256(p) for p in [parent/'pilot_results.json',parent/'pilot_contract.json',
                parent/'full_R2_0_coefficients.npy',parent/'full_R2_1_coefficients.npy',
                parent/'full_R2_0_selected.npy',parent/'full_R2_1_selected.npy']},
            'selection_hashes':{p.name:sha256(p) for p in [OUTPUT/'selected_grid_rows.npy',OUTPUT/'selected_grid_difference.npy']}}
    (OUTPUT/'pilot_contract.json').write_text(json.dumps(contract,indent=2)+'\n')
    outcomes=[]
    cases=[('full_R2',None,14)]
    if not full_only:
        cases.append(('reduced_support_diagnostic',contract['restricted_license_diagnostic_columns'],7))
    for label,columns,budget in cases:
        for repeat in range(2):
            m=None
            try:
                m,beta,z=build_model(a,b,w,budget=budget,columns=columns,seconds=seconds,env=env,grid_difference=grid_difference)
                for i in beta:
                    value=.8 if i==0 else .2 if i==288 else .5 if i in (289,290,291) else 0.
                    if starts is not None:
                        value=float(starts[repeat,i])
                    beta[i].Start=value; z[i].Start=float(value!=0)
                    if start_selections is not None:
                        z[i].Start=float(start_selections[repeat,i])
                if repeat==0:
                    m.write(str(OUTPUT/(label+'.lp')))
                m.optimize()
                outcome={'label':label,'repeat':repeat,'status':m.Status,'solution_count':m.SolCount,'runtime_seconds':m.Runtime}
                if m.SolCount:
                    coeff=np.zeros(292); selected=np.zeros(292,dtype=bool)
                    for i in beta:
                        coeff[i]=beta[i].X; selected[i]=z[i].X>.5
                    audit=audit_solution(a,b,w,coeff,selected,model_name='R2',budget=budget,grid_difference=grid_difference)
                    if grid_difference is not None:
                        outcome['grid_max_kcal_mol']={g:float(np.max(np.abs(np.load(OUTPUT/f'grid_difference_{g}.npy')@coeff))*627.5094740631) for g in ('99590','75302')}
                    outcome.update(audit=audit,objective=m.ObjVal,bound=m.ObjBound)
                    outcome.update(gap_report(m.ObjVal,m.ObjBound,m.MIPGap))
                    outcome['solver_diagnostics']={'ObjBoundC':m.ObjBoundC,'ObjCon':m.ObjCon,
                        'IsMIP':m.IsMIP,'IsMultiObj':m.IsMultiObj,'NumObj':m.NumObj,
                        'requested_MIPGap':m.Params.MIPGap,'requested_MIPGapAbs':m.Params.MIPGapAbs,
                        'gurobi_version':gp.gurobi.version(),
                        'getAttr_gap':gap_report(m.getAttr('ObjVal'),m.getAttr('ObjBound'),m.getAttr('MIPGap'))}
                    outcome['objective_agrees']=bool(np.isclose(m.ObjVal,audit['weighted_sse_hartree2'],rtol=1e-7,atol=1e-10))
                    np.save(OUTPUT/f'{label}_{repeat}_coefficients.npy',coeff)
                    np.save(OUTPUT/f'{label}_{repeat}_selected.npy',selected)
                outcomes.append(outcome)
            except gp.GurobiError as exc:
                outcomes.append({'label':label,'repeat':repeat,'gurobi_error':exc.errno})
            finally:
                if m is not None: m.dispose()
    report={'step':15,'status':'preparation_complete_full_pilot_pending' if any('gurobi_error' in r for r in outcomes) else 'bounded_pilot_finished',
            'R1_data_ready':False,'outcomes':outcomes,'output':str(OUTPUT),'bulk_submission_authorized':False}
    (OUTPUT/'pilot_results.json').write_text(strict_dumps(report)+'\n')
    print(strict_dumps(report))
    return 0 if all(r.get('audit',{}).get('passed',False) and r.get('objective_agrees',False) for r in outcomes) else 1


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=OUTPUT)
    parser.add_argument('--wls',action='store_true')
    parser.add_argument('--seconds',type=int,choices=(2,60),default=2)
    parser.add_argument('--full-only',action='store_true')
    parser.add_argument('--grid-pass2',type=Path)
    args=parser.parse_args()
    if args.wls:
        # No default-environment fallback and no credential-bearing startup logs.
        try:
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
                result=main(args.output,env,args.seconds,args.full_only,args.grid_pass2)
        except Exception as exc:
            print(json.dumps({'error_type':type(exc).__name__,
                              'gurobi_error':exc.errno if isinstance(exc,gp.GurobiError) else None}))
            result=1
        raise SystemExit(result)
    raise SystemExit(main(args.output,seconds=args.seconds,full_only=args.full_only,grid_pass2=args.grid_pass2))
