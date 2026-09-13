"""One isolated resource pilot, fail closed and retain per-stage evidence."""
from pathlib import Path
import json,hashlib,shutil,os,subprocess,time,sys,re,struct,importlib.util
import numpy as np
from step8_validation_helpers import parse_matrix,scalar
from validate_step6 import parse_pt2
R=Path(__file__).resolve().parents[1];DATA=Path('/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2');SCR=Path('/clusterfs/mhg-data/yaoshen/scf_read/coach_mp2/step10_v1')
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 return h.hexdigest()
def write(p,d):
 tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n');tmp.replace(p)
def size(p):return sum(f.stat().st_size for f in p.rglob('*') if f.is_file())
def hf(t):return scalar(t,r'Alpha\s+Exchange\s+Energy')+scalar(t,r'Beta\s+Exchange\s+Energy')
def base(t):return sum(scalar(t,k) for k in [r'One-Electron\s+Energy',r'Total\s+Coulomb\s+Energy',r'Nuclear\s+Repu\.\s+Energy'])
def main(tier):
 protocol=R/'manifests/step10_protocol_v1.json';p=json.loads(protocol.read_text());c=next(c for c in p['cases'] if c['tier']==tier);name=c['species'];H=DATA/'step10_v1'/tier;H.mkdir(parents=True,exist_ok=False);(H/'tmp').mkdir()
 report=dict(tier=tier,species=name,job_id=os.environ['SLURM_JOB_ID'],protocol_sha256=sha(protocol),status='running',stages=[]);rp=H/'summary.json';write(rp,report)
 try:
  for f,h in p['authority_sha256'].items():assert sha(R/f)==h
  b=json.loads((R/'manifests/step8_build_v1.json').read_text());assert sha(b['binary'])==b['binary_sha256'] and sha(b['libks'])==b['libks_sha256']
  env=os.environ.copy();env.update(QC='/clusterfs/mhg/yaoshen/qchem/trunk',QCPROG=b['binary'],QCAUX='/global/home/groups-sw/mhg/qchem_public/qchem_620/qcaux',QCSCRATCH=str(SCR),TMPDIR=str(H/'tmp'),LD_LIBRARY_PATH=str(Path(b['libks']).parent)+':'+env.get('LD_LIBRARY_PATH',''))
  env.pop('QCLOCALSCR',None);env.pop('QCHEM_DUMP_INTEGRATED_DV_INPUTS',None);env.pop('QCHEM_PRINT_INTEGRATED_DV',None)
  libs=subprocess.check_output(['ldd',b['binary']],env=env,text=True);assert b['libks'] in libs;(H/'loaded_libraries.txt').write_text(libs)
  src=DATA/'step5_import_v1/species'/name;receipt=json.loads((src/'import.json').read_text());files=[f for f in ['53.0','54.0','58.0','819.0','99.0','molecule','pseudodata'] if (src/f).is_file()];start=time.monotonic();hashes={f:sha(src/f) for f in files};assert all(h==receipt['sha256'][f] for f,h in hashes.items());report.update(source_hash_seconds=time.monotonic()-start,source_hashes=hashes,copy_bytes=sum((src/f).stat().st_size for f in files));write(rp,report)
  texts={}
  for stage in c['stages']:
   mode=stage['mode'];tag=name+'_'+mode;dst=SCR/tag;dst.mkdir(parents=True,exist_ok=False);start=time.monotonic()
   for f,h in hashes.items():shutil.copyfile(src/f,dst/f);assert sha(dst/f)==h
   rec=dict(mode=mode,copy_verify_seconds=time.monotonic()-start);inp=Path(stage['input']);assert sha(inp)==stage['sha256'];out=H/(mode+'.out');timing=H/(mode+'.time');e=env.copy()
   if mode.isdigit():e['QCHEM_PRINT_INTEGRATED_DV']='1'
   start=time.monotonic()
   with (H/(mode+'.driver.log')).open('w') as log:
    ret=subprocess.run(['/usr/bin/time','-v','-o',str(timing),env['QC']+'/bin/qchem','-save','-nt',str(c['cpus']),str(inp),str(out),tag],cwd=H,env=e,stdout=log,stderr=subprocess.STDOUT)
   rec.update(wall_seconds=time.monotonic()-start,exit_code=ret.returncode,retained_scratch_bytes=size(dst));report['stages'].append(rec);write(rp,report);assert ret.returncode==0
   t=out.read_text();texts[mode]=t;assert 'Thank you very much for using Q-Chem' in t and 'The orbitals will not be altered' in t and 'COACH_MP2: preserving saved MOs' in t;assert sha(dst/'53.0')==hashes['53.0']
   n,m,*_=struct.unpack('<4i',(src/'819.0').read_bytes());coef=np.fromfile(src/'53.0',dtype='<f8')[:2*n*m].reshape(2,m,n);den=np.fromfile(dst/'54.0',dtype='<f8').reshape(2,n,n);occ=re.findall(r'There are\s+(\d+) alpha and\s+(\d+) beta electrons',t);assert len(set(occ))==1
   for s,o in enumerate(map(int,occ[0])):
    error=float(np.max(abs(coef[s,:o].T@coef[s,:o]-den[s])));assert error<=16*np.finfo(float).eps*np.sum(coef[s,:o]**2)
   if mode.isdigit():a,count=parse_matrix(t);np.save(H/(mode+'_selected.npy'),a.T[[64,154,166]].reshape(288));rec['complete_matrix_blocks']=count
   if mode=='RIMP2':rec['pt2']=parse_pt2(t,'RIMP2')
   peak=re.search(r'Maximum resident set size \(kbytes\):\s*(\d+)',timing.read_text());assert peak;rec.update(peak_rss_kib=int(peak[1]),output_bytes=out.stat().st_size,output_sha256=sha(out),MO_bytes_unchanged=True,density_pass=True,passed=True);write(rp,report);print(name,mode,'PASS',rec['wall_seconds'],flush=True)
  sr,lr,full=[texts[k] for k in ['sr_vv','lr_hf','full_hf']];fixed=base(full)+hf(lr);split=hf(sr)+hf(lr)-hf(full);assert abs(split)<=1e-8
  errors={g:fixed+.22878981*hf(sr)+scalar(texts[g],r'DFT\s+Exchange\s+Energy')+scalar(texts[g],r'DFT\s+Correlation\s+Energy')-scalar(texts[g],r'SCF\s+energy') for g in ['250974','99590','75302']};assert max(map(abs,errors.values()))<=1e-8
  ref=R.parent/'revwb97m2/qchem_scalar_features.py';spec=importlib.util.spec_from_file_location('readonly_d4',ref);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);start=time.monotonic();atm=mod.evaluate_d4_atm_from_qchem_input(Path(c['stages'][0]['input']).read_text())
  assert all(sha(src/f)==h for f,h in hashes.items());report.update(status='native_stages_passed_accounting_and_capacity_review_pending',native_passed=True,hf_split_error=split,parent_errors=errors,d4_atm=atm,d4_seconds=time.monotonic()-start,d4_helper_sha256=sha(ref),retained_output_bytes=size(H));write(rp,report)
 except Exception as e:
  report.update(status='failed_requires_review',error=repr(e));write(rp,report);raise
if __name__=='__main__':main(sys.argv[1])
