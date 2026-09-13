"""Isolated incremental Q-Chem link; shared source/build inputs are read-only."""
from pathlib import Path
import subprocess,shlex,hashlib,json,os,shutil
R=Path(__file__).resolve().parents[1];Q=Path('/clusterfs/mhg/yaoshen/qchem/trunk');B=Q/'build';D=Path('/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2/build/step5_no_orientation_v1')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 return h.hexdigest()
def main():
 D.mkdir(parents=True,exist_ok=False);os.environ['TMPDIR']=str(D)
 source=Q/'scfman/scfman.C';old=source.read_text();needle='if ( !(LPSCFMI > 0 && LPCorr==0) && rem_read(REM_SMX_SOLVATION) != -1)';assert old.count(needle)==1
 new=old.replace(needle,'if (NoSCF) printf("COACH_MP2: preserving saved MOs; skipping post-SCF orientation\\n");\n    if (!NoSCF && !(LPSCFMI > 0 && LPCorr==0) && rem_read(REM_SMX_SOLVATION) != -1)')
 patched=R/'runtime/step5_scfman.C';patched.write_text(new)
 flags={}
 for line in (B/'scfman/CMakeFiles/scfman.dir/flags.make').read_text().splitlines():
  if ' = ' in line:
   k,v=line.split(' = ',1);flags[k]=shlex.split(v)
 link=shlex.split((B/'CMakeFiles/qcprog.exe.dir/link.txt').read_text());compiler=link[0]
 pins={str(p):sha(p) for p in [source,B/'scfman/libscfman.a',B/'scfman/CMakeFiles/scfman.dir/flags.make',B/'CMakeFiles/qcprog.exe.dir/link.txt']}
 obj=D/'scfman.C.o';cmd=[compiler]+flags['CXX_DEFINES']+flags['CXX_INCLUDES']+flags['CXX_FLAGS']+['-I'+str(Q/'scfman'),'-c',str(patched),'-o',str(obj)]
 print('Compiling project-local scfman object',flush=True);subprocess.run(cmd,cwd=D,check=True)
 lib=D/'libscfman.a';shutil.copyfile(B/'scfman/libscfman.a',lib);subprocess.run(['ar','r',str(lib),str(obj)],cwd=D,check=True)
 for i,t in enumerate(link):
  if i and link[i-1]=='-o':link[i]=str(D/'qcprog.exe');continue
  p=B/t
  if not t.startswith('-') and p.is_file():
   link[i]=str(lib if p==B/'scfman/libscfman.a' else p)
   if p.suffix in ['.a','.o','.so']:pins[str(p)]=sha(p)
 print('Linking with read-only existing dependencies',flush=True);subprocess.run(link,cwd=D,check=True)
 assert all(sha(Path(p))==h for p,h in pins.items()),'shared build changed'
 manifest=dict(binary=str(D/'qcprog.exe'),binary_sha256=sha(D/'qcprog.exe'),source_pins=pins,patched_source=str(patched),patched_sha256=sha(patched),compile_command=cmd,link_command=link,scope='Skip only post-SCF orientation when NoSCF; no shared writes; source SCF/energy kernels otherwise unchanged')
 (R/'manifests/step5_no_orientation_build_v1.json').write_text(json.dumps(manifest,indent=2)+'\n');print('BUILD PASS',flush=True)
if __name__=='__main__':main()
