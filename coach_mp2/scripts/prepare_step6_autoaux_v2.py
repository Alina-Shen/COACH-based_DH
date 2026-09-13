from pathlib import Path
import json,shutil,hashlib
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 d=json.loads((R/'manifests/step6_autoaux_diagnostic_v1.json').read_text());c=dict(d['cases'][0]);text=Path(c['input']).read_text();start=text.index('$aux_basis');lines=text[start:].splitlines()
 for i,line in enumerate(lines):
  parts=line.split()
  if len(parts)==2:
   try:a,b=map(float,parts)
   except ValueError:continue
   lines[i]=f'{a:.16e} {b:.16e}'
 text=text[:start]+'\n'.join(lines)+'\n';c['tag']+='_v2';p=R/'inputs/step6_v1'/(c['tag']+'.in');p.write_text(text);c.update(input=str(p.resolve()),input_sha256=sha(p));dst=Path(c['scratch']).parent/c['tag'];dst.mkdir();c['scratch']=str(dst)
 for f,h in c['source_hashes'].items():shutil.copyfile(Path(c['source'])/f,dst/f);assert sha(dst/f)==h
 d['cases']=[c];d['format_amendment']='Print all primitive exponents/coefficients as explicit floating-point literals; v1 rejected integer 1 by Q-Chem strict real parser; same generated basis.';(R/'manifests/step6_autoaux_diagnostic_v2.json').write_text(json.dumps(d,indent=2)+'\n')
if __name__=='__main__':main()
