from pathlib import Path
import json,struct
import numpy as np
from validate_step6 import parse_pt2,sha,H
from validate_step2_fixed import parse as parent_parse
from step6_numerics import spectrum
R=Path(__file__).resolve().parents[1]
def main():
 mp=parse_pt2((H/'16_C_AE18_MP2_4center_FC.out').read_text(),'MP2');baseline=parent_parse((H/'16_C_AE18_RIMP2_FC.out').read_text());cases=json.loads((R/'manifests/step6_diagnostics_v1.json').read_text())['cases']+json.loads((R/'manifests/step6_autoaux_diagnostic_v2.json').read_text())['cases'];rows=[]
 for c in cases:
  out=H/(c['tag']+'.out');t=out.read_text();src=Path(c['source']);dst=Path(c['scratch']);assert sha(Path(c['input']))==c['input_sha256'];assert all(sha(src/k)==h for k,h in c['source_hashes'].items())
  if 'Thank you very much' not in t:
   assert c['tag'].endswith('_legacy') and 'get_id_dft_path error!' in t;rows.append(dict(tag=c['tag'],status='failed_before_PT2',reason='COACH DFT path unsupported with USE_LIBQINTS FALSE',output_sha256=sha(out)));continue
  p=parent_parse(t);v=parse_pt2(t,'RIMP2');assert abs(p['energy_hartree']-baseline['energy_hartree'])<=2e-8;assert sha(dst/'53.0')==c['source_hashes']['53.0'];assert '# of frozen core orbitals: 1' in t
  n,m,*_=struct.unpack('<4i',(src/'819.0').read_bytes());coef=np.fromfile(src/'53.0',dtype='<f8')[:2*n*m].reshape(2,m,n);f=np.fromfile(dst/'58.0',dtype='<f8').reshape(2,n,n);ref=np.fromfile(Path('/clusterfs/mhg-data/yaoshen/scf_read/coach_mp2/step5_native_v2/16_C_AE18/58.0'),dtype='<f8').reshape(2,n,n);err=max(float(abs(spectrum(coef[s],f[s],o)[0]-spectrum(coef[s],ref[s],o)[0]).max()) for s,o in enumerate([4,2]));assert err<=2e-8
  delta=(v['doubles']-mp['doubles'])*627.50947406;rows.append(dict(tag=c['tag'],status='normal',pt2=v,ri_minus_conventional_kcalmol=delta,within_predeclared_accuracy=abs(delta)<=.015,MO_file_unchanged=True,source_hashes_unchanged=True,parent_energy_difference=p['energy_hartree']-baseline['energy_hartree'],native_spectrum_difference=err,output_sha256=sha(out)))
 d=dict(scope='Diagnostics only; original auxiliary authority remains unchanged',cases=rows);(R/'results/step6_diagnostics.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d,indent=2))
if __name__=='__main__':main()
