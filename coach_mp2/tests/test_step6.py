import unittest,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from validate_step6 import parse_pt2,H
from step6_numerics import denominator_ranges,spectrum
class Step6(unittest.TestCase):
 def test_actual_ri_singles_excluded(self):
  t=(H/'16_C_AE18_RIMP2_FC.out').read_text();p=parse_pt2(t,'RIMP2');self.assertAlmostEqual(p['doubles'],p['same_spin']+p['opposite_spin']);self.assertNotEqual(p['doubles'],p['printed_total'])
 def test_reject_wrong_engine(self):
  with self.assertRaises(ValueError):parse_pt2((H/'SIE4x4_h2o_MP2_FC.out').read_text(),'MP2')
 def test_reject_wrong_scale(self):
  t=(H/'16_C_AE18_RIMP2_FC.out').read_text().replace('factor = 1.000000','factor = 0.340960')
  with self.assertRaises(ValueError):parse_pt2(t,'RIMP2')
 def test_reject_broken_spin_total(self):
  t=(H/'16_C_AE18_RIMP2_FC.out').read_text().replace('-0.0891768698','-0.1891768698')
  with self.assertRaises(ValueError):parse_pt2(t,'RIMP2')
 def test_invalid_denominator(self):
  for e in [np.array([0.,0.]),np.array([1.,0.]),np.array([float('nan'),1.])]:
   with self.assertRaises(ValueError):denominator_ranges([e,e],[1,1],0)
 def test_frozen_core_window(self):
  e=np.array([-10.,-1.,1.]);a=denominator_ranges([e,e],[2,2],0);b=denominator_ranges([e,e],[2,2],1);self.assertEqual(a['ab']['min'],-22.);self.assertEqual(b['ab']['min'],-4.)
 def test_spectrum_keeps_occupied_virtual_separate(self):
  e,ov=spectrum(np.eye(2),np.array([[-1.,.1],[.1,1.]]),1);np.testing.assert_allclose(e,[-1,1]);self.assertEqual(ov,.1)
if __name__=='__main__':unittest.main()
