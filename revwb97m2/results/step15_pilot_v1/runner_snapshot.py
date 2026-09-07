"""Prepare named optimizer inputs and run bounded C0 solver diagnostics."""
import json
from pathlib import Path
import numpy as np
import gurobipy as gp
from revwb97m2.qchem_scalar_features import sha256
from revwb97m2.mio import feature_names,build_model,audit_solution

ROOT=Path(__file__).resolve().parents[1]
OUTPUT=ROOT/'results/step15_pilot_v1'


def main():
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
              'code_sha256':{str(p):sha256(p) for p in [ROOT/'mio.py',Path(__file__)]},
              'profile':'C0_minimal_critical','full_R2_budget':14,'seconds_per_solve':2,'threads':1,'seed':0,
              'repeats':2,'purpose':'engineering_smoke_not_coefficient_selection',
              'restricted_license_diagnostic_columns':[0,8,96,104,192,200,288,289,290,291],
              'restricted_license_diagnostic_budget':7,'bulk_submission_authorized':False,
              'feature_matrix_sha256':sha256(OUTPUT/'feature_matrix.npy')}
    (OUTPUT/'pilot_contract.json').write_text(json.dumps(contract,indent=2)+'\n')
    outcomes=[]
    for label,columns,budget in [('full_R2',None,14),('reduced_support_diagnostic',contract['restricted_license_diagnostic_columns'],7)]:
        for repeat in range(2):
            m=None
            try:
                m,beta,z=build_model(a,b,w,budget=budget,columns=columns,seconds=2)
                for i in beta:
                    value=.8 if i==0 else .2 if i==288 else .5 if i in (289,290,291) else 0.
                    beta[i].Start=value; z[i].Start=float(value!=0)
                if repeat==0:
                    m.write(str(OUTPUT/(label+'.lp')))
                m.optimize()
                outcome={'label':label,'repeat':repeat,'status':m.Status,'solution_count':m.SolCount,'runtime_seconds':m.Runtime}
                if m.SolCount:
                    coeff=np.zeros(292); selected=np.zeros(292,dtype=bool)
                    for i in beta:
                        coeff[i]=beta[i].X; selected[i]=z[i].X>.5
                    audit=audit_solution(a,b,w,coeff,selected,model_name='R2',budget=budget)
                    outcome.update(audit=audit,objective=m.ObjVal,bound=m.ObjBound,gap=m.MIPGap)
                    outcome['objective_agrees']=bool(np.isclose(m.ObjVal,audit['weighted_sse_hartree2'],rtol=1e-7,atol=1e-10))
                    np.save(OUTPUT/f'{label}_{repeat}_coefficients.npy',coeff)
                outcomes.append(outcome)
            except gp.GurobiError as exc:
                outcomes.append({'label':label,'repeat':repeat,'gurobi_error':exc.errno,'message':str(exc)})
            finally:
                if m is not None: m.dispose()
    report={'step':15,'status':'preparation_complete_full_pilot_pending' if any('gurobi_error' in r for r in outcomes) else 'bounded_pilot_finished',
            'R1_data_ready':False,'outcomes':outcomes,'output':str(OUTPUT),'bulk_submission_authorized':False}
    (OUTPUT/'pilot_results.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
