"""Tiny installation smoke test only; no production fit or Gurobi dependency."""
from pathlib import Path
import json,sys,hashlib,importlib.metadata,platform,subprocess
import numpy as np
from pyscipopt import Model
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 model=Model('scip_installation_smoke');model.printVersion();model.printExternalCodeVersions();model.hideOutput()
 config=json.loads((R/'configs/scip_pilot_v1.json').read_text());requested={'limits/time':7200.,'limits/memory':32768.,'limits/gap':1e-4,'limits/absgap':1e-10,'numerics/feastol':1e-9,'parallel/maxnthreads':16}
 for k,v in requested.items():model.setParam(k,v)
 effective={k:model.getParam(k) for k in requested}
 # Tight certification overrides only for the tiny installation test.
 model.setParam('limits/gap',0.);model.setParam('limits/absgap',0.)
 # Analytical optimum: z=1, x=2, objective=.1; z=0 gives4.
 x=model.addVar('x',lb=0,ub=3);z=model.addVar('z',vtype='B');t=model.addVar('t',lb=0)
 model.addCons(x<=3*z);model.addCons((x-2)*(x-2)+.1*z<=t);model.setObjective(t)
 model.optimize();status=str(model.getStatus());values=dict(x=model.getVal(x),z=model.getVal(z),t=model.getVal(t));residual_objective=(values['x']-2)**2+.1*values['z']
 print('Smoke diagnostic:',status,values,residual_objective,model.getObjVal(),flush=True)
 assert status=='optimal' and abs(values['z']-1)<1e-9 and abs(values['x']-2)<1e-4 and abs(residual_objective-.1)<1e-8 and abs(model.getObjVal()-.1)<1e-7
 # Verify installed numeric stack can read native feature arrays, without a fit.
 v=json.loads((R/'results/step8_validation.json').read_text());h=Path(v['output']);meta=json.loads((h/'manifest.json').read_text());assert sha(h/'manifest.json')==v['feature_manifest_sha256']
 for f,s in meta['sha256'].items():assert sha(h/f)==s and np.load(h/f).shape==(292,)
 report=dict(passed=True,scope='installation, mixed-integer quadratic epigraph known-optimum smoke and existing-feature readback only',python=sys.version,platform=platform.platform(),packages={p:importlib.metadata.version(p) for p in ['pyscipopt','numpy','scipy']},scip_version=[model.getMajorVersion(),model.getMinorVersion(),model.getTechVersion()],requested_parameters=requested,effective_pilot_parameters=effective,smoke_only_overrides={'limits/gap':0.,'limits/absgap':0.},normal_solve_threads_note='parallel/maxnthreads is a ceiling for parallel mode, not a guarantee that optimize uses 16 threads',status=status,solution=values,residual_objective=residual_objective,reported_objective=model.getObjVal(),gap=model.getGap(),dual_bound=model.getDualbound(),native_feature_arrays_read=10,production_fit_run=False,gurobi_used=False)
 (R/'results/scip_pilot_install_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
