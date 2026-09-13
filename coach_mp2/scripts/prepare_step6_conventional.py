from pathlib import Path
import json,re,shutil,hashlib
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 d=json.loads((R/'manifests/step6_protocol_v1.json').read_text());cases=[]
 for c in d['cases']:
  if c['engine']!='MP2':continue
  c=dict(c);c['tag']=c['species']+'_MP2_4center_FC';p=R/'inputs/step6_v1'/(c['tag']+'.in');p.write_text(re.sub(r'(?im)^AUX_BASIS_CORR\s+.*\n','',Path(c['input']).read_text()));c.update(input=str(p.resolve()),input_sha256=sha(p));dst=Path(c['scratch']).parent/c['tag'];dst.mkdir();c['scratch']=str(dst)
  for f,h in c['source_hashes'].items():shutil.copyfile(Path(c['source'])/f,dst/f);assert sha(dst/f)==h
  cases.append(c)
 d['cases']=cases;d['amendment']='Remove auxiliary basis only for genuine conventional four-center reference; first nominal MP2 runs actually used RI and are diagnostics only.';d['denominators']='Native engines pseudocanonicalize COACH Fock in unchanged occupied/virtual spaces. Compare projected native Fock spectra and denominator ranges to Step5 COACH-only reference, not blindly to saved 53.0 eigenvalues.';d['native_fock_spectrum_tolerance_hartree']=2e-8
 (R/'manifests/step6_conventional_v2.json').write_text(json.dumps(d,indent=2)+'\n')
if __name__=='__main__':main()
