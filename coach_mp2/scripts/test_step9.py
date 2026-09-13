import unittest,importlib.util,ast
from pathlib import Path
import numpy as np
import step9_constraints as c

def seed():
 b=np.zeros(292);b[0]=.85;b[288:]=[.15,.2,.3,.4];z=(b!=0).astype(float);return b,z
class ConstraintsTests(unittest.TestCase):
 def test_reference_ueg_and_nonconstant_legendre(self):
  spec=importlib.util.spec_from_file_location('reference_mio',c.ROOT.parent/'revwb97m2/mio.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  np.testing.assert_array_equal(c.ueg_vector(),m.ueg_vector('R2'))
  b,z=seed();b[16]=2;b[0]+=1;z[16]=1;self.assertTrue(c.audit(b,z,14)['passed']);self.assertNotEqual(b[0]+b[288],1)
 def test_matrix_and_witness(self):
  b,z=seed();m=c.build_constraints(14);x=np.r_[b,z]
  self.assertEqual(m['A_ub'].shape,(585,584));self.assertTrue(np.all(m['A_ub']@x<=m['b_ub']));np.testing.assert_allclose(m['A_eq']@x,m['b_eq']);self.assertTrue(np.all(x>=m['lower']) and np.all(x<=m['upper']))
  b[1]=.1;x=np.r_[b,z];self.assertGreater((m['A_ub']@x-m['b_ub']).max(),0)
 def test_support_includes_zero_sr(self):
  b,z=seed();b[0]=1;b[288]=0;self.assertTrue(c.audit(b,z,5)['passed']);self.assertFalse(c.audit(b,z,4)['passed']);z[288]=0;self.assertFalse(c.audit(b,z,5)['passed'])
 def test_independent_scalars_and_rejections(self):
  b,z=seed();self.assertTrue(c.audit(b,z,14)['passed'])
  for j,val in [(0,.84),(289,0),(290,1.1),(291,-.1)]:
   bad=b.copy();bad[j]=val;self.assertFalse(c.audit(bad,z,14)['passed'])
  z[1]=.5;self.assertFalse(c.audit(b,z,14)['passed'])
 def test_grid_public_has_no_slack(self):
  b,z=seed();d=np.zeros((2,292));d[:,289]=[c.PUBLIC/.2*1.01,c.PUBLIC/.2*.5]
  a=c.audit(b,z,14,difference=d,rows=np.array([1]));self.assertTrue(a['passed']);self.assertEqual(a['full_grid_violations'],[0])
  self.assertFalse(c.audit(b,z,14,difference=d,rows=np.array([0]))['passed'])
  d[0,289]=c.PUBLIC/.2*1.00000001;self.assertFalse(c.audit(b,z,14,difference=d,rows=np.array([0]))['passed'])
  d[0,289]=c.PUBLIC/.2*.9995;self.assertTrue(c.audit(b,z,14,difference=d,rows=np.array([0]))['passed']);m=c.build_constraints(14,phase='selected',difference=d,rows=np.array([0]));self.assertGreater((m['A_ub']@np.r_[b,z]-m['b_ub']).max(),0)
 def test_selection_matches_reference_ties_duplicates_remaining(self):
  source=(c.ROOT.parent/'revwb97m2/selective_grid_v1.py').read_text();tree=ast.parse(source);f=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='select_rows');scope={'np':np};exec(compile(ast.Module(body=[f],type_ignores=[]),'reference','exec'),scope)
  rng=np.random.default_rng(19);d=rng.integers(-2,3,(450,292)).astype(float);b=np.zeros((138,292));b[:,0]=1;b[::2,1]=1
  np.testing.assert_array_equal(c.select_rows(d,b),scope['select_rows'](d,b));self.assertTrue(len(c.select_rows(d,b))>=300)
 def test_invalid_inputs(self):
  for args in [dict(phase='discovery',difference=np.zeros((2,292))),dict(phase='selected'),dict(phase='selected',difference=np.zeros((2,292)),rows=np.array([0,0]))]:
   with self.assertRaises(ValueError):c.build_constraints(14,**args)
  with self.assertRaises(ValueError):c.audit(np.full(292,np.nan),np.zeros(292),14)
  with self.assertRaises(ValueError):c.select_rows(np.zeros((2,291)),np.zeros((138,292)))
 def test_dense_factors_independent_polynomials(self):
  b,z=seed();b[:288]=0;b[1]=2;b[96+8]=3;b[192+1]=4
  f=c.dense_factors(b)['factors'];self.assertEqual(f['exchange']['min'],0);self.assertEqual(f['exchange']['max'],2);self.assertEqual(f['same_spin']['min'],-3);self.assertEqual(f['same_spin']['max'],3);self.assertEqual(f['opposite_spin']['min'],0);self.assertEqual(f['opposite_spin']['max'],4)
if __name__=='__main__':unittest.main()
