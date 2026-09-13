import unittest,json,sys,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from complete_step6 import check,R
class Completion(unittest.TestCase):
 def setUp(self):
  self.v=json.loads((R/'results/step6_validation.json').read_text());self.d=json.loads((R/'results/step6_denominator_audit.json').read_text());self.a=dict(species='16_C_AE18',retained_auxiliary_basis='rimp2-def2-QZVPPD',observed_error_hartree=-.00014789149999999696)
 def test_exact_user_exception(self):self.assertTrue(check(self.v,self.d,self.a));self.assertFalse(self.v['passed'])
 def test_other_species_failure(self):
  self.v['comparisons'][0]['passed']=False
  with self.assertRaises(ValueError):check(self.v,self.d,self.a)
 def test_changed_error(self):
  self.a['observed_error_hartree']=0
  with self.assertRaises(ValueError):check(self.v,self.d,self.a)
 def test_denominator_failure(self):
  self.d['cases'][0]['passed']=False
  with self.assertRaises(ValueError):check(self.v,self.d,self.a)
 def test_core_failure(self):
  self.v['comparisons'][1]['all_electron_minus_frozen_core']=1
  with self.assertRaises(ValueError):check(self.v,self.d,self.a)
if __name__=='__main__':unittest.main()
