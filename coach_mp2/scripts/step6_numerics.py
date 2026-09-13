"""Independent denominator/space audit using Q-Chem-native AO ordering."""
import numpy as np

def spectrum(coeff,fock,occ):
 projected=coeff@fock@coeff.T
 blocks=[projected[:occ,:occ],projected[occ:,occ:]]
 energies=[]
 for b in blocks:
  off=b-np.diag(np.diag(b))
  # Match native is_diag threshold, including its retained ordering.
  energies.extend((np.linalg.eigvalsh(b) if np.any(abs(off)>1e-13) else np.diag(b)).tolist())
 return np.array(energies),float(np.max(np.abs(projected[:occ,occ:])))
def denominator_ranges(energies,occupations,core):
 gaps=[e[core:o,None]-e[None,o:] for e,o in zip(energies,occupations)]
 # SS extrema conservatively include Pauli-excluded equal-index pairs.
 result={}
 for label,a,b in [('aa',0,0),('ab',0,1),('bb',1,1)]:
  x,y=gaps[a],gaps[b]
  if not x.size or not y.size:result[label]=dict(empty=True);continue
  lo=float(x.min()+y.min());hi=float(x.max()+y.max())
  if not (np.isfinite(x).all() and np.isfinite(y).all() and hi<0):raise ValueError('Nonfinite/nonnegative PT2 denominator')
  result[label]=dict(min=lo,max=hi,min_absolute=-hi,empty=False)
 return result
