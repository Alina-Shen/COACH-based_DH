from pathlib import Path
import json,hashlib,shutil
from step4_authority import setrem
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 base=next(c for c in json.loads((R/'manifests/step6_protocol_v1.json').read_text())['cases'] if c['tag']=='16_C_AE18_RIMP2_FC');cases=[]
 for name,settings in [('legacy',{'USE_LIBQINTS':'FALSE'}),('augQZ',{'AUX_BASIS_CORR':'rimp2-aug-cc-pVQZ'})]:
  c=dict(base);c['tag']='16_C_AE18_RIMP2_'+name;c['diagnostic_only']=True;text=Path(base['input']).read_text()
  for k,v in settings.items():text=setrem(text,k,v)
  p=R/'inputs/step6_v1'/(c['tag']+'.in');p.write_text(text);c.update(input=str(p.resolve()),input_sha256=sha(p));dst=Path(base['scratch']).parent/c['tag'];dst.mkdir();c['scratch']=str(dst)
  for f,h in c['source_hashes'].items():shutil.copyfile(Path(c['source'])/f,dst/f);assert sha(dst/f)==h
  cases.append(c)
 (R/'manifests/step6_diagnostics_v1.json').write_text(json.dumps(dict(scope='Investigate failed carbon RI/conventional gate; no authoritative basis/engine amendment',cases=cases),indent=2)+'\n')
if __name__=='__main__':main()
