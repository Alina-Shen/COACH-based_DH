import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from check_step5_native_v4 import close_scf_components
from validate_step2_fixed import parse
class EnergyClosure(unittest.TestCase):
 def test_actual_nonzero_dispersion_native_output(self):
  p=Path('/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2/step5_native_v2/ISOL24_i8e.out')
  result=close_scf_components(parse(p.read_text()))
  self.assertAlmostEqual(result['dispersion_hartree'],-0.0000622332,places=12)
  self.assertLess(abs(result['closure_error_hartree']),2e-8)
 def test_idempotent_and_nonmutating(self):
  data=dict(component_sum_hartree=-10.,dispersion_hartree=-.1,energy_hartree=-10.)
  result=close_scf_components(data)
  self.assertEqual(result,close_scf_components(result))
  self.assertEqual(result['component_sum_hartree'],-10.)
  self.assertEqual(result['dispersion_hartree'],-.1)
  self.assertNotIn('closure_convention',data)
if __name__=='__main__':unittest.main()
