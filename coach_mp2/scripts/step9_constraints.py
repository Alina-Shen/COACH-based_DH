"""Solver-neutral C0 constraints. Variables are [beta(292), z(292)]."""
from pathlib import Path
import json
import numpy as np
from scipy import sparse
ROOT=Path(__file__).resolve().parents[1]
SPEC=json.loads((ROOT/'configs/scientific_spec_v1.json').read_text())
N=292
PUBLIC=SPEC['grids']['threshold_kcal_per_mol']/SPEC['units']['hartree_to_kcal_per_mol']
INTERNAL=PUBLIC*SPEC['grids']['internal_safety_factor']

def vector(x):
 x=np.asarray(x,dtype=float)
 if x.shape!=(N,) or not np.isfinite(x).all():raise ValueError('Expected finite 292-vector')
 return x

def grid_data(d,rows):
 d=np.asarray(d,dtype=float);rows=np.asarray(rows)
 if d.ndim!=2 or d.shape[1]!=N or not np.isfinite(d).all():raise ValueError('Invalid grid matrix')
 if rows.ndim!=1 or not np.issubdtype(rows.dtype,np.integer) or len(np.unique(rows))!=len(rows) or np.any(rows<0) or np.any(rows>=len(d)):raise ValueError('Invalid selected row identities')
 return d,rows

def ueg_vector():
 a=np.zeros(N);a[np.arange(12)*8]=np.polynomial.legendre.legvander(0.,11).ravel();a[288]=1
 return a

def coefficient_bounds():
 lo=np.full(N,-25.);hi=np.full(N,25.);lo[288:]=[0,1e-8,1e-8,1e-8];hi[288:]=[1,.99999999,.99999999,.99999999]
 return lo,hi

def build_constraints(budget,*,phase='discovery',difference=None,rows=None):
 if type(budget) is not int or not 4<=budget<=N:raise ValueError('Invalid K')
 if phase not in ('discovery','selected'):raise ValueError('Invalid phase')
 if phase=='discovery' and (difference is not None or rows is not None):raise ValueError('Discovery has no grid constraints')
 if phase=='selected':
  if difference is None or rows is None:raise ValueError('Selected phase requires frozen row identities')
  difference,rows=grid_data(difference,rows)
  if not len(rows):raise ValueError('Selected phase cannot silently omit grid rows')
 lo,hi=coefficient_bounds();lower=np.r_[lo,np.zeros(N)];upper=np.r_[hi,np.ones(N)];lower[N+288:]=1
 eye=sparse.eye(N,format='csr');blocks=[sparse.hstack([eye,-25*eye]),sparse.hstack([-eye,-25*eye]),sparse.csr_matrix(np.r_[np.zeros(N),np.ones(N)][None,:])];rhs=[np.zeros(2*N),np.array([budget])]
 if phase=='selected':
  g=sparse.hstack([sparse.csr_matrix(difference[rows]),sparse.csr_matrix((len(rows),N))]);blocks.extend([g,-g]);rhs.append(np.full(2*len(rows),INTERNAL))
 return dict(A_ub=sparse.vstack(blocks,format='csr'),b_ub=np.concatenate(rhs),A_eq=sparse.csr_matrix(np.r_[ueg_vector(),np.zeros(N)][None,:]),b_eq=np.ones(1),lower=lower,upper=upper,integrality=np.r_[np.zeros(N,dtype=int),np.ones(N,dtype=int)])

def select_rows(difference,candidates,per_candidate=100,additional=200):
 d,_=grid_data(difference,np.array([],dtype=int));c=np.asarray(candidates,dtype=float)
 if c.ndim!=2 or c.shape[1]!=N or not len(c) or not np.isfinite(c).all() or type(per_candidate) is not int or type(additional) is not int or min(per_candidate,additional)<0:raise ValueError('Invalid selection input')
 chosen=set()
 for beta in c:chosen.update(np.argsort(np.abs(d@beta))[::-1][:per_candidate].tolist())
 remaining=np.asarray(sorted(set(range(len(d)))-chosen),dtype=int)
 if len(remaining) and additional:chosen.update(remaining[np.argsort(np.abs(d[remaining]).sum(axis=1))[::-1][:additional]].tolist())
 return np.asarray(sorted(chosen),dtype=int)

def audit(beta,z,budget,*,difference=None,rows=None):
 beta=vector(beta);z=vector(z)
 if type(budget) is not int or not 4<=budget<=N:raise ValueError('Invalid K')
 lo,hi=coefficient_bounds()
 # Full-precision readback: exact binary support; reference feasibility tolerances.
 checks=dict(binary=bool(np.all((z==0)|(z==1))),support=bool(z.sum()<=budget),mandatory=bool(np.all(z[288:]==1)),semilocal_bounds=bool(np.all(abs(beta[:288])<=25+1e-8)),scalar_bounds=bool(np.all(beta[288:]>=lo[288:]-1e-9) and np.all(beta[288:]<=hi[288:]+1e-9)),unselected_zero=bool(np.all(abs(beta[z==0])<=1e-9)),ueg=bool(abs(ueg_vector()@beta-1)<=1e-10))
 report=dict(checks=checks,ueg_residual=float(ueg_vector()@beta-1))
 if difference is not None:
  if rows is None:raise ValueError('Rows required for selected-only acceptance')
  d,rows=grid_data(difference,rows);values=abs(d@beta);checks['selected_grid']=bool(np.all(values[rows]<=PUBLIC))
  report.update(selected_internal_limit_satisfied=bool(np.all(values[rows]<=INTERNAL)),full_grid_violations=np.flatnonzero(values>PUBLIC).tolist(),full_grid_max_hartree=float(values.max(initial=0)),review_required=bool(np.any(values>PUBLIC)))
 elif rows is not None:raise ValueError('Grid matrix required')
 report['passed']=all(checks.values());return report

def dense_factors(beta,points=101):
 """Sample polynomial enhancement factors only; report extrema, impose no bounds."""
 beta=vector(beta)
 if type(points) is not int or points<2:raise ValueError('Invalid mesh')
 u=np.linspace(0,1,points);v=np.linspace(-1,1,points);up=np.polynomial.polynomial.polyvander(u,7);ul=np.polynomial.legendre.legvander(u,7);vl=np.polynomial.legendre.legvander(v,11)
 result={}
 for i,name in enumerate(('exchange','same_spin','opposite_spin')):
  f=vl@beta[i*96:(i+1)*96].reshape(12,8)@(ul if i==2 else up).T
  mn=np.unravel_index(np.argmin(f),f.shape);mx=np.unravel_index(np.argmax(f),f.shape)
  result[name]=dict(min=float(f[mn]),max=float(f[mx]),min_at=[float(u[mn[1]]),float(v[mn[0]])],max_at=[float(u[mx[1]]),float(v[mx[0]])])
 return dict(points_per_axis=points,domain='u=[0,1], companion=[-1,1]',quantity='polynomial enhancement factor; excludes density-dependent prefactors',diagnostic_only=True,factors=result)
