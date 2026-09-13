"""Validate and publish Step9 solver-neutral pilot artifacts, without fitting."""
from pathlib import Path
import json,hashlib,importlib.metadata
import numpy as np
from scipy import sparse
import step9_constraints as c
R=c.ROOT

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
def main():
 freeze=R/'manifests/step8_freeze_v1.json'
 for f,h in json.loads(freeze.read_text())['sha256'].items():assert sha(R/f)==h,f
 report8=json.loads((R/'results/step8_validation.json').read_text());H=Path(report8['output']);meta=json.loads((H/'manifest.json').read_text());assert sha(H/'manifest.json')==report8['feature_manifest_sha256']
 for f,h in meta['sha256'].items():assert sha(H/f)==h,f
 assert '\nOK\n' in (R/'results/step9_tests.log').read_text()
 beta=np.zeros(292)
 for k,v in c.SPEC['optimization']['starts']['simple_nonzero_coefficients'].items():beta[int(k)]=v
 z=(beta!=0).astype(float);base=c.audit(beta,z,14);assert base['passed']
 matrices={g:np.stack([np.load(H/(s+'_delta_'+g+'.npy')) for s in ['SIE4x4_h2o','16_C_AE18']]) for g in ['99590','75302']}
 # Native molecular rows are a pilot exercise, not the later reaction-row selection.
 selected=np.arange(2);a=c.build_constraints(14,phase='selected',difference=matrices['99590'],rows=selected);d=c.build_constraints(14)
 out=R/'results/step9_constraint_pilot_v1';out.mkdir(exist_ok=True)
 sparse.save_npz(out/'selected_A_ub.npz',a['A_ub']);sparse.save_npz(out/'A_eq.npz',a['A_eq']);sparse.save_npz(out/'discovery_A_ub.npz',d['A_ub'])
 np.savez(out/'bounds_rhs.npz',lower=a['lower'],upper=a['upper'],integrality=a['integrality'],selected_b_ub=a['b_ub'],discovery_b_ub=d['b_ub'],b_eq=a['b_eq'],ueg=c.ueg_vector(),pilot_rows=selected)
 dense=c.dense_factors(beta);write(out/'simple_seed_dense_factors.json',dense)
 contract=dict(schema_version=1,step=9,profile='C0_minimal_critical',solver_backend=None,variable_order='beta[0:292], binary_z[0:292]',feature_columns=meta['columns'],big_M=25,ueg='sum_w P_w(0)*beta_exchange[8*w] + beta[288] = 1',mandatory_slots=[288,289,290,291],support='sum(z)<=K; all four scalar slots count, including zero SRHF',coefficient_bounds={'semilocal':[-25,25],'SRHF':[0,1],'VV10_PT2_ATM':[1e-8,.99999999]},cross_scalar_equalities=[],grid=dict(discovery='none',selected='frozen selected 99590-minus-250974 reaction rows only',public_limit_hartree=c.PUBLIC,internal_limit_hartree=c.INTERNAL,public_slack_hartree=0,diagnostic_grid='75302; report only',full_grid_violations='report for review, not automatic rejection',selection='all 138 validated discovery candidates, preserving duplicates; union top100 abs(D beta) each, then top200 remaining L1; NumPy argsort reversed, freeze identities before pass2',actual_selection_status='pending real discoveries at Step15; pilot rows are not production selection'),audit_tolerances={'UEG':1e-10,'semilocal_bound':1e-8,'scalar_bound_and_unselected_zero':1e-9,'binary_readback':'exact 0 or 1'},dense_factors='101x101 sample on u=[0,1], companion=[-1,1]; diagnostic only, no sampled bounds or one-electron bound',scientific_spec_sha256=sha(R/'configs/scientific_spec_v1.json'),step8_freeze_sha256=sha(freeze))
 write(R/'configs/step9_constraint_contract_v1.json',contract)
 reports={g:c.audit(beta,z,14,difference=matrices[g],rows=selected) for g in matrices}
 result=dict(step=9,passed=True,solver_used=False,tests=8,pilot='frozen simple algorithmic seed; not a fitted or optimized candidate',simple_seed_C0=base,native_molecular_grid_diagnostics=reports,production_grid_selection_frozen=False,discovery_matrix_shape=list(d['A_ub'].shape),selected_pilot_matrix_shape=list(a['A_ub'].shape),dense_factor_report=str(out/'simple_seed_dense_factors.json'),numpy_version=np.__version__,scipy_version=importlib.metadata.version('scipy'),reference_sha256={str(p):sha(p) for p in [R.parent/'revwb97m2/mio.py',R.parent/'revwb97m2/selective_grid_v1.py',R.parent/'revwb97m2/fit_spec.py']},native_feature_manifest_sha256=sha(H/'manifest.json'))
 write(R/'results/step9_validation.json',result)
 files=[R/'scripts/step9_constraints.py',R/'scripts/test_step9.py',Path(__file__),R/'configs/step9_constraint_contract_v1.json',R/'results/step9_validation.json',R/'results/step9_tests.log']+sorted(out.iterdir())
 write(R/'manifests/step9_freeze_v1.json',dict(step=9,sha256={str(p.relative_to(R)):sha(p) for p in files},step8_freeze_sha256=sha(freeze)))
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
