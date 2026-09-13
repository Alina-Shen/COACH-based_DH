import importlib.util,json,struct,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('fixed',ROOT/'scripts/validate_step2_fixed.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
class FixedTests(unittest.TestCase):
 def text(self):return (mod.OUT/'SIE4x4_h2o_fixed.out').read_text()
 def test_actual_output(self):self.assertLess(abs(mod.parse(self.text())['closure_error_hartree']),2e-8)
 def test_truncated_output_rejected(self):
  with self.assertRaises(ValueError):mod.parse(self.text().replace('Thank you very much for using Q-Chem',''))
 def test_missing_bypass_rejected(self):
  with self.assertRaises(ValueError):mod.parse(self.text().replace('The orbitals will not be altered',''))
 def test_missing_component_rejected(self):
  with self.assertRaises(KeyError):mod.parse(self.text().replace('One-Electron','Unknown'))
 def test_density_change_rejected(self):
  with tempfile.TemporaryDirectory(dir=ROOT/'runtime') as tmp:
   p=Path(tmp);c=[1.,0.,0.,1.]*2+[-1.,1.]*2;density=[1.,0.,0.,0.]*2
   for name,values in [('mo',c),('src',density),('out',density)]: (p/name).write_bytes(struct.pack('<'+'d'*len(values),*values))
   self.assertTrue(mod.density_audit(p/'mo',p/'src',p/'out',2,[1,1])['passed'])
   density[0]+=1e-10;(p/'out').write_bytes(struct.pack('<8d',*density))
   self.assertFalse(mod.density_audit(p/'mo',p/'src',p/'out',2,[1,1])['passed'])
 def test_nonfinite_rejected(self):
  with tempfile.TemporaryDirectory(dir=ROOT/'runtime') as tmp:
   p=Path(tmp)
   for name,values in [('mo',[float('nan')]*12),('src',[0.]*8),('out',[0.]*8)]: (p/name).write_bytes(struct.pack('<'+'d'*len(values),*values))
   with self.assertRaises(ValueError):mod.density_audit(p/'mo',p/'src',p/'out',2,[1,1])
if __name__=='__main__':unittest.main()
