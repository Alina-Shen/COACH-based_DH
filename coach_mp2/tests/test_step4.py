import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from audit_step4_inputs import parse
from step4_authority import setrem,derive
from validate_step4_snapshot import check_transformation
BASE='$molecule\n0 1\nH 0 0 0\nH 0 0 1\n$end\n$rem\nMETHOD DSD-PBEPBE-D3\nUNRESTRICTED TRUE\nBASIS DEF2-QZVPPD\nAUX_BASIS_CORR rimp2-def2-QZVPPD\nXC_GRID 000099000590\n$end\n'
class InputTests(unittest.TestCase):
 def test_valid_cartesian(self):self.assertEqual(len(parse(BASE)[-1]),2)
 def test_nan_rejected(self):
  with self.assertRaises(ValueError):parse(BASE.replace('H 0 0 1','H nan 0 1'))
 def test_missing_rem_rejected(self):
  with self.assertRaises(ValueError):parse(BASE.split('$rem')[0])
 def test_duplicate_blocks_rejected(self):
  with self.assertRaises(ValueError):parse(BASE+BASE)
 def test_conflicting_rem_rejected(self):
  with self.assertRaises(ValueError):parse(BASE.replace('METHOD DSD-PBEPBE-D3','METHOD COACH\nMETHOD HF'))
 def test_concatenated_line_rejected(self):
  with self.assertRaises(ValueError):parse(BASE.replace('METHOD DSD-PBEPBE-D3','SCF_GUESS SADMOSCF_CONVERGENCE 7'))
 def test_incomplete_fragment_rejected(self):
  with self.assertRaises(ValueError):parse(BASE.replace('H 0 0 1','H 0 0 1\n--'))
 def test_method_only(self):
  target=setrem(BASE,'METHOD','COACH');check_transformation(BASE,target,'sample','gscdb137')
 def test_geometry_mutation_rejected(self):
  with self.assertRaises(ValueError):check_transformation(BASE,setrem(BASE,'METHOD','COACH').replace('H 0 0 1','H 0 0 2'),'sample','gscdb137')
 def test_grid_mutation_rejected(self):
  with self.assertRaises(ValueError):check_transformation(BASE,setrem(BASE,'METHOD','COACH').replace('000099000590','000075000302'),'sample','gscdb137')
 def test_new_ecp_rejected(self):
  with self.assertRaises(ValueError):check_transformation(BASE,setrem(BASE,'METHOD','COACH')+'$ecp\nH 0\n$end\n','sample','gscdb137')
 def test_known_line_repair(self):
  text=BASE.replace('XC_GRID','SCF_GUESS SADMOSCF_CONVERGENCE 7\nXC_GRID')
  derived,changes,_=derive(text,'BH9_05_17TS',{'scope':'gscdb137'})
  self.assertEqual(parse(derived)[1]['SCF_CONVERGENCE'],'7');self.assertIn('split_concatenated_rem_line',changes)
 def test_external_auxiliary_explicit(self):
  source=BASE.replace('AUX_BASIS_CORR rimp2-def2-QZVPPD\n','')
  derived,_,_=derive(source,'sample',{'scope':'BigNC_external'});check_transformation(source,derived,'sample','BigNC_external')
  with self.assertRaises(ValueError):check_transformation(source,derived.replace('rimp2-def2-TZVPPD','invented'),'sample','BigNC_external')
 def test_ghost_preserved(self):
  source=BASE.replace('H 0 0 1','@H 0 0 1');derived=setrem(source,'METHOD','COACH')
  check_transformation(source,derived,'sample','gscdb137');self.assertEqual(parse(derived)[-1][1][0],'@H')
 def test_method_key_boundary(self):
  source=BASE.replace('METHOD DSD-PBEPBE-D3','METHOD_EXTRA 1\nMETHOD DSD-PBEPBE-D3');self.assertIn('METHOD_EXTRA 1',setrem(source,'METHOD','COACH'))
if __name__=='__main__':unittest.main()
