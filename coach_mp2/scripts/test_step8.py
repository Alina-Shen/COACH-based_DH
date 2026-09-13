import unittest,struct,tempfile
from pathlib import Path
import numpy as np
from step8_validation_helpers import parse_matrix,iter_diagnostic
from step8_reference.integrated_dv import selected_integrated_dv_block,KernelParameters
from step8_reference.qchem_integrated_dv_reference import full_integrated_dv_block
class GatewayTests(unittest.TestCase):
 def test_matrix_rejects_incomplete_and_nonfinite(self):
  good='COACH integratedDV begin rows=96 cols=180\nintegratedDV\n'+'\n'.join([' '.join(['0']*180)]*96)+'\nCOACH integratedDV end\n'
  self.assertEqual(parse_matrix(good)[0].shape,(96,180))
  for bad in [good.replace('COACH integratedDV end',''),good.replace('0','nan',1),good.replace('rows=96','rows=95'),good.replace('integratedDV\n','integratedDV\n0\n')]:
   with self.assertRaises(ValueError):parse_matrix(bad)
 def test_dump_rejects_truncation_and_trailing_bytes(self):
  with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]/'results') as d:
   p=Path(d)/'dump';p.write_bytes(b'COACHDV1'+struct.pack('=Q',0));self.assertEqual(list(iter_diagnostic(p)),[])
   for raw in [b'COACHDV1',b'COACHDV1'+struct.pack('=Q',1),b'COACHDV1'+struct.pack('=Q',0)+b'x']:
    p.write_bytes(raw)
    with self.assertRaises(ValueError):list(iter_diagnostic(p))
 def test_rows_and_omega_sensitivity(self):
  a=(np.array([.2,.3]),np.array([.2,.4]),np.array([.1,.2]),np.ones((2,3))*.12,np.ones((2,3))*.08,np.array([.3,.5]),np.array([.2,.4]))
  x=selected_integrated_dv_block(*a);full=full_integrated_dv_block(*a).T[[64,154,166]]
  np.testing.assert_allclose(x,full,rtol=2e-12,atol=2e-12)
  wrong=selected_integrated_dv_block(*a,parameters=KernelParameters(omega=.30))
  self.assertGreater(np.max(abs(x-wrong)),1e-5)
if __name__=='__main__':unittest.main()
