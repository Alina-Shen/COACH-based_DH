"""Collect terminal accounting and native evidence; never submit/retry jobs."""
from pathlib import Path
import json,subprocess,hashlib
R=Path(__file__).resolve().parents[1];H=Path('/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2/step10_v1')
def main():
 jobs=json.loads((R/'manifests/step10_jobs_v1.json').read_text());records=[]
 raw=subprocess.check_output(['sacct','-j',','.join(jobs.values()),'--parsable2','--noheader','--format=JobID,State,ExitCode,ElapsedRaw,TotalCPU,MaxRSS,ReqMem,AllocCPUS,NodeList'],text=True)
 (R/'results/step10_accounting.txt').write_text(raw)
 accounting={x.split('|')[0]:x.split('|')[1:] for x in raw.splitlines()}
 for tier,job in jobs.items():
  p=H/tier/'summary.json';s=json.loads(p.read_text()) if p.exists() else {};a=accounting.get(job,[]);terminal=bool(a and a[0]=='COMPLETED' and a[1]=='0:0');ok=terminal and s.get('native_passed',False) and len(s.get('stages',[]))==7 and all(x.get('passed',False) for x in s.get('stages',[]))
  records.append(dict(tier=tier,job=job,accounting=a,native_status=s.get('status','not_started'),passed=bool(ok),summary_sha256=hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None,measured_peak_rss_mib=max([x.get('peak_rss_kib',0)/1024 for x in s.get('stages',[])],default=0),native_wall_seconds=sum(x.get('wall_seconds',0) for x in s.get('stages',[]))))
 d=dict(step=10,native_and_accounting_passed=all(x['passed'] for x in records),capacity_signoff=False,records=records,remaining_gate='Review all terminal measurements, retained storage and coverage before resource guidance/signoff; no class-wide downsizing from three samples',solver_required=False)
 (R/'results/step10_progress.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d,indent=2))
if __name__=='__main__':main()
