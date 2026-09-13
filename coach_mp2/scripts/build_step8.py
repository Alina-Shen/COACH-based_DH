"""Isolated COACH feature-export port; no writes to either shared Q-Chem tree."""
from pathlib import Path
import json,hashlib,shlex,subprocess,shutil,os
R=Path(__file__).resolve().parents[1];Q=Path('/clusterfs/mhg/yaoshen/qchem/trunk');P=Path('/clusterfs/mhg-data/yaoshen/qchem/trunk');B=Q/'build';D=Path('/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2/build/step8_features_v1');S=R/'runtime/step8_source'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 return h.hexdigest()
def main():
 D.mkdir(parents=True,exist_ok=False);os.environ['TMPDIR']=str(D);pins={};commands=[]
 for rel in ['libks/qchem/ks_main.C','libks/libks/drivers/ks_driver_exc.C','libks/libks/exc_fxc/integrated_dv.C','libks/libks/exc_fxc/integrated_dv.h']:
  p=P/rel;pins[str(p)]=sha(p);s=p.read_text()
  if rel.endswith('ks_main.C'):
   old='if (!check_xcfunc(XCFunc) && rem_read(REM_SNK) <= 0) return false;';assert s.count(old)==1;s=s.replace(old,'if (rem_read(REM_USE_LIBQINTS) == 0) return false;\n    if (!check_xcfunc(XCFunc)) return false;')
  if rel.endswith('integrated_dv.C'):assert s.count('double omega = 0.3;')==1;s=s.replace('double omega = 0.3;','double omega = 0.27;')
  p=S/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)
 step5=json.loads((R/'manifests/step5_no_orientation_build_v1.json').read_text());compiler=step5['link_command'][0]
 objs={}
 for rel,group in [('libks/qchem/ks_main.C','libks/qchem/CMakeFiles/qchem5_ks.dir'),('libks/libks/drivers/ks_driver_exc.C','libks/libks/CMakeFiles/ks.dir'),('libks/libks/exc_fxc/integrated_dv.C','libks/libks/CMakeFiles/ks.dir')]:
  flags=B/group/'flags.make';pins[str(flags)]=sha(flags);vals={k:shlex.split(v) for line in flags.read_text().splitlines() if ' = ' in line for k,v in [line.split(' = ',1)]};obj=D/(Path(rel).name+'.o');cmd=[compiler,'-I'+str(S/'libks'),'-I'+str((Q/rel).parent)]+vals['CXX_DEFINES']+vals['CXX_INCLUDES']+vals['CXX_FLAGS']+['-c',str(S/rel),'-o',str(obj)];commands.append(cmd);subprocess.run(cmd,cwd=D,check=True);objs[rel]=obj
 def resolve_link(tokens,root,target,replacements):
  out=[]
  for i,t in enumerate(tokens):
   if i and tokens[i-1]=='-o':out.append(str(target));continue
   p=root/t
   if not t.startswith('-') and p.is_file():
    p=p.resolve();pins[str(p)]=sha(p);t=str(replacements.get(str(p),p))
   out.append(t)
  return out
 lp=B/'libks/libks/CMakeFiles/ks.dir/link.txt';pins[str(lp)]=sha(lp)
 replace={str((B/'libks/libks/CMakeFiles/ks.dir/drivers/ks_driver_exc.C.o').resolve()):objs['libks/libks/drivers/ks_driver_exc.C']}
 cmd=resolve_link(shlex.split(lp.read_text()),B/'libks/libks',D/'libks.so',replace);cmd.append(str(objs['libks/libks/exc_fxc/integrated_dv.C']));commands.append(cmd);subprocess.run(cmd,cwd=D,check=True)
 libold=B/'libks/qchem/libqchem5_ks.a';pins[str(libold)]=sha(libold);lib=D/'libqchem5_ks.a';shutil.copyfile(libold,lib);subprocess.run(['ar','r',str(lib),str(objs['libks/qchem/ks_main.C'])],cwd=D,check=True)
 # Reuse Step5's already validated NoSCF object/archive and all other dependencies.
 cmd=list(step5['link_command']);cmd[cmd.index('-o')+1]=str(D/'qcprog.exe')
 for i,t in enumerate(cmd):
  if t==str(libold):cmd[i]=str(lib)
  if t==str(B/'libks/libks/libks.so'):cmd[i]=str(D/'libks.so')
 cmd.insert(1,'-Wl,-rpath,'+str(D));commands.append(cmd);subprocess.run(cmd,cwd=D,check=True)
 assert all(sha(Path(p))==h for p,h in pins.items())
 report=dict(binary=str(D/'qcprog.exe'),binary_sha256=sha(D/'qcprog.exe'),libks=str(D/'libks.so'),libks_sha256=sha(D/'libks.so'),parent_build_manifest_sha256=sha(R/'manifests/step5_no_orientation_build_v1.json'),source_and_link_pins=pins,local_sources={str(p):sha(p) for p in S.rglob('*') if p.is_file()},commands=commands,scope='Feature emission only; retain original COACH libks availability and Step5 NoSCF guard; omega .27 gamma_ss .01; opt-in native density export')
 (R/'manifests/step8_build_v1.json').write_text(json.dumps(report,indent=2)+'\n');print('BUILD PASSED')
if __name__=='__main__':main()
