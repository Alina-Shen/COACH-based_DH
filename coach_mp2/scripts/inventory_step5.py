"""Read-only COACH legacy archive inventory; no inferred method/build provenance."""
from pathlib import Path
import csv,json,struct,math,collections,concurrent.futures,hashlib
ROOT=Path(__file__).resolve().parents[1]
SOURCES={'BigNC_external':Path('/global/scratch/users/jsliang/BigNC/COACH')}
DEFAULT=Path('/global/scratch/users/jsliang/COACH3')
def atoms(text):
 lines=text.lower().split('$molecule',1)[1].split('$end',1)[0].strip().splitlines()
 result=[];charge,spin=map(int,lines[0].split())
 for line in lines[1:]:
  v=line.split()
  if len(v)==4:
   xyz=tuple(float(x) for x in v[1:])
   if not all(math.isfinite(x) for x in xyz):raise ValueError('nonfinite geometry')
   result.append((v[0],xyz))
  elif len(v)!=2 and v!=['--']:raise ValueError('malformed molecule line')
 return charge,spin,result

def audit(r):
 name=r['species'];p=SOURCES.get(r['scope'],DEFAULT)/name
 out=dict(species=name,scope=r['scope'],source=str(p),status='missing',issues='',bytes=0,nbasis='',nmo='',files=0,geometry_max_error='')
 if not p.is_dir():return out
 issues=[];files=[]
 for f in p.iterdir():
  if f.is_symlink():issues.append('symlink:'+f.name)
  elif f.is_file():files.append(f)
 out['bytes']=sum(f.stat().st_size for f in files);out['files']=len(files)
 try:
  dims=struct.unpack('<4i',(p/'819.0').read_bytes());n,m=dims[:2];out.update(nbasis=n,nmo=m)
  if n!=int(r['orbital_spherical_aos']):issues.append('basis_dimension')
  if not 0<m<=n:issues.append('mo_dimension')
  for fn,size in [('53.0',16*m*(n+1)),('54.0',16*n*n),('58.0',16*n*n)]:
   if (p/fn).stat().st_size!=size:issues.append(fn+'_size')
  a,b=atoms((p/'molecule').read_text()),atoms(Path(r['source']).read_text())
  if a[:2]!=b[:2] or [x[0] for x in a[2]]!=[x[0] for x in b[2]]:issues.append('geometry_identity')
  else:
   error=max((abs(x-y) for aa,bb in zip(a[2],b[2]) for x,y in zip(aa[1],bb[1])),default=0)
   out['geometry_max_error']=error
   if not math.isfinite(error) or error>1e-10:issues.append('geometry_coordinates')
 except Exception as e:issues.append(type(e).__name__+':'+str(e))
 out.update(status='quarantine' if issues else 'structural_pass',issues=';'.join(issues))
 return out

def main():
 from active_input_authority import load_rows
 rows=load_rows()
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(audit,rows))
 with (ROOT/'manifests/step5_inventory_v1.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(results[0]));w.writeheader();w.writerows(results)
 summary=dict(total=len(rows),status=dict(collections.Counter(r['status'] for r in results)),total_available_bytes=sum(r['bytes'] for r in results),issues=dict(collections.Counter(r['issues'] for r in results if r['issues'])),scope_status=dict(collections.Counter(r['scope']+':'+r['status'] for r in results)),method_identity='user attribution and Step2 baseline only; historical outputs/build unavailable',basis_identity='dimensions only; legacy archive does not contain full basis definition',solver_required=False)
 (ROOT/'results/step5_inventory_v1.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
