"""Guard against false component-closure passes and one-electron conventions."""
import importlib.util
from pathlib import Path
import unittest
p=Path(__file__).resolve().parents[1]/'scripts/audit_step2_baseline.py'
spec=importlib.util.spec_from_file_location('audit',p)
audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
class BaselineTests(unittest.TestCase):
    def fixture(self,name):
        return audit.parse((audit.REF/'FunctionalCOACH/tests/qchem_outputs'/f'{name}.out').read_text())
    def test_water_closes(self):
        self.assertTrue(audit.closure(self.fixture('SIE4x4_h2o'))['passed'])
    def test_carbon_kinetic_attraction_convention(self):
        self.assertTrue(audit.closure(self.fixture('16_C_AE18'))['passed'])
    def test_missing_component_rejected(self):
        vals=self.fixture('SIE4x4_h2o');del vals['DFT Non-Local Correlation Energy']
        with self.assertRaises(KeyError):audit.closure(vals)
    def test_perturbed_component_fails(self):
        vals=self.fixture('SIE4x4_h2o');vals['DFT Exchange Energy']+=1e-5
        self.assertFalse(audit.closure(vals)['passed'])
    def test_fortran_exponent(self):
        self.assertEqual(audit.parse(' A  Energy = -1.25D+02 hartrees')['A Energy'],-125)
if __name__=='__main__':unittest.main()
