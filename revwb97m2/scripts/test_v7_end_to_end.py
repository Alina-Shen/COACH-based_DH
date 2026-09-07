"""Bounded synthetic CLI integration test; never chemical validation evidence."""
import argparse
import json
import subprocess
import sys
from pathlib import Path
import numpy as np
from revwb97m2.fit_spec import load_fit_settings
from revwb97m2.fit_inputs import ARRAYS, digest


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();out=args.output
    out.mkdir(parents=True,exist_ok=False)
    s=load_fit_settings()
    a=np.zeros((4,292));a[:,288:]=np.eye(4)
    d=np.zeros_like(a);d[:,0]=5e-5
    arrays=dict(feature_matrix=a,target=np.array([.2,.3,.4,.5]),objective_weight=np.ones(4),
                grid_difference_99590=d,grid_difference_75302=2*d)
    artifacts={}
    for name,value in arrays.items():
        p=out/(name+'.npy');np.save(p,value)
        artifacts[name]={'path':p.name,'sha256':digest(p)}
    evidence=out/'assembly.json'
    evidence.write_text(json.dumps({'passed':True,'purpose':'synthetic_test_only',
        'scientific_specification_sha256':s.specification_sha256,
        'array_sha256':{name:artifacts[name]['sha256'] for name in ARRAYS}}))
    artifacts['assembly_validation']={'path':evidence.name,'sha256':digest(evidence)}
    manifest={'schema_version':1,'status':'validated','purpose':'synthetic_test_only',
        'scientific_specification_sha256':s.specification_sha256,'role':'coefficient_fitting',
        'weights_policy':'coach_si_table2_final_cycle','reaction_ids':[f'SYNTHETIC_{i}' for i in range(4)],
        'energy_parameters':{'omega':.3,'gamma_ss':.01,'vv10_b':5.5,'vv10_c':.01},
        'vv10_grid_policy':'single_grid_zero_difference','vv10_grid_zero_reason':'synthetic test',
        'artifacts':artifacts}
    path=out/'inputs.json';path.write_text(json.dumps(manifest))
    base=[sys.executable,'-m','revwb97m2.scripts.run_v7_fit','--manifest',str(path),
          '--budget','14','--seconds','10','--threads','1']
    checks={}
    def invoke(label,extra):
        result=subprocess.run(base+extra,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        # Never echo credential-bearing raw subprocess exceptions.
        checks[label]=result.returncode==0
        return checks[label]
    p1,p2,restart=(out/name for name in ('pass1','pass2','restart'))
    if not invoke('pass1',['--output',str(p1)]):
        raise RuntimeError('synthetic pass1 failed; inspect sanitized failure record')
    if not invoke('pass2',['--output',str(p2),'--start',str(p1),'--grid-candidates',str(p1)]):
        raise RuntimeError('synthetic pass2 failed; inspect sanitized failure record')
    invoke('restart',['--output',str(restart),'--start',str(p2),'--grid-candidates',str(p1)])
    original=digest(p2/'result.json')
    invoke('resume',['--output',str(p2),'--start',str(p1),'--grid-candidates',str(p1),'--resume'])
    checks['resume_did_not_overwrite']=digest(p2/'result.json')==original
    c1=np.load(p1/'coefficients.npy');c2=np.load(p2/'coefficients.npy')
    checks['pass1_violates_grid']=bool(np.max(np.abs(d@c1))>s.grid_public_limit)
    checks['pass2_public_limit']=bool(np.max(np.abs(d@c2))<=s.grid_public_limit)
    # Other exchange-basis coefficients also enter UEG: the optimizer need not
    # change SR-HF specifically to satisfy this synthetic grid constraint.
    checks['coefficients_changed']=bool(np.max(np.abs(c2-c1))>1e-4)
    for name,p in [('pass1',p1),('pass2',p2)]:
        c=np.load(p/'coefficients.npy');r=json.loads((p/'result.json').read_text())
        exact=float(np.sum((a@c-arrays['target'])**2)+1e-10*(c@c))
        checks[name+'_objective']=bool(abs(r['objective']-exact)<1e-10)
    # Tampered array refusal must occur without a new published run.
    np.save(out/'target.npy',np.ones(4))
    checks['tamper_rejected']=not invoke('tampered_should_fail',['--output',str(out/'tampered')])
    del checks['tampered_should_fail']
    np.save(out/'target.npy',arrays['target'])
    checks['input_restored']=digest(out/'target.npy')==artifacts['target']['sha256']
    report={'passed':all(checks.values()),'checks':checks,'purpose':'synthetic_only_not_real_data',
            'specification_sha256':s.specification_sha256}
    (out/'integration_report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    return 0 if report['passed'] else 1


if __name__=='__main__':
    raise SystemExit(main())
