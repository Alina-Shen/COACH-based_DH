"""Prepare bounded native resource pilots; never submit or copy source orbitals."""
from pathlib import Path
import json,csv,tarfile,re,hashlib
from step4_authority import setrem
from active_input_authority import load_rows
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 rows={x['species']:x for x in load_rows()};ptr=json.loads((R/'manifests/step4_snapshot_v1.json').read_text());cases=[];folder=R/'inputs/step10_v1';folder.mkdir(exist_ok=False)
 configs=[('small','3d4dIPSS_Ag_GS',8,14,7000,'02:00:00','mhg','mhg','normal'),('medium','TMB28_C1',8,62,30000,'08:00:00','mhg','mhg','normal'),('high','MOR32_pr24',16,557,300000,'48:00:00','lr8','lr_mhg2','mhg2_lr8_normal')]
 with tarfile.open(Path(ptr['snapshot'])/'inputs.tar') as tar:
  for tier,name,cpu,mem,qmem,wall,part,account,qos in configs:
   row=rows[name];base=tar.extractfile('coach/'+name+'.in').read().decode();assert hashlib.sha256(base.encode()).hexdigest()==row['derived_sha256']
   for k,v in dict(METHOD='COACH',SCF_GUESS='READ',SCF_GUESS_MIX=0,GEN_SCFMAN='FALSE',MAX_SCF_CYCLES=0,MP2_RESTART_NO_SCF='TRUE',NO_ORTHO='TRUE',SCF_FINAL_PRINT=1,MEM_TOTAL=qmem,MEM_STATIC=min(8000,qmem//8),XC_GRID='000250000974').items():base=setrem(base,k,v)
   stages=[]
   for mode in ['250974','99590','75302','sr_vv','full_hf','lr_hf','RIMP2']:
    text=base
    if mode.isdigit():text=setrem(setrem(text,'XC_GRID',{'250974':'000250000974','99590':'000099000590','75302':'000075000302'}[mode]),'XC_FXC',3)
    elif mode=='RIMP2':
     text=re.sub(r'(?im)^METHOD\s+.*\n','',text)
     for k,v in json.loads((R/'configs/step6_runtime_authority_v1.json').read_text())['controls'].items():text=setrem(text,k,v)
    else:
     text=re.sub(r'(?im)^(METHOD|AUX_BASIS_CORR)\s+.*\n','',text);text=setrem(text,'EXCHANGE','HF')
     if mode!='full_hf':
      for k,v in dict(LRC_DFT='TRUE',SRC_DFT='TRUE',OMEGA=270,OMEGA2=270,HF_SR=1000 if mode=='sr_vv' else 0,HF_LR=0 if mode=='sr_vv' else 1000).items():text=setrem(text,k,v)
     if mode=='sr_vv':
      for k,v in dict(NL_CORRELATION='VV10',NL_GRID=1,NL_VV_B=550,NL_VV_C=100,NL_VV_SCALE=100000).items():text=setrem(text,k,v)
    p=folder/(name+'_'+mode+'.in');p.write_text(text);stages.append(dict(mode=mode,input=str(p.resolve()),sha256=sha(p)))
   c=dict(tier=tier,species=name,cpus=cpu,memory_gib=mem,qchem_memory_mb=qmem,walltime=wall,partition=part,account=account,qos=qos,ao=int(row['orbital_spherical_aos']),aux_ao=int(row['auxiliary_spherical_aos']),stages=stages);cases.append(c)
   script=f'''#!/bin/bash
#SBATCH --job-name=coach_s10_{tier}
#SBATCH --partition={part}
#SBATCH --account={account}
#SBATCH --qos={qos}
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task={cpu}
#SBATCH --mem={mem}G
#SBATCH --time={wall}
#SBATCH --output={R}/results/step10_{tier}_%j.log
set -euo pipefail
export OMP_NUM_THREADS={cpu} MKL_NUM_THREADS={cpu} OPENBLAS_NUM_THREADS={cpu}
export PYTHONDONTWRITEBYTECODE=1
/global/home/users/yaoshen/.conda/envs/dh/bin/python -B {R}/scripts/run_step10.py {tier}
'''
   (R/'slurm'/('run_step10_'+tier+'.sh')).write_text(script)
 refs=[R.parent/'revwb97m2/manifests/qchem_gateway/q6_resource_guidance_v1.yaml',R.parent/'revwb97m2/manifests/qchem_gateway/q6_resource_pilots_v1.yaml']
 d=dict(step=10,status='prepared_not_measured',solver_required=False,omega=.27,scope='three fitting-species size tiers; seven native stages each plus geometry-only D4; no bulk production',selection='same small/medium/high species as reference Q6; measured reference costs are guidance only',resource_rationale='retain reference 14/62/557 GiB and 8/8/16 CPUs; high wall increased to48h for additional scalar/RI stages; small/medium use available mhg, high requires lr8 memory',retry_policy='no automatic retry; preserve failed evidence',measurement=['source/copy hash time and bytes','per-stage wall and GNU-time peak RSS','post-stage retained scratch bytes (not peak scratch)','native validity, MO/density invariance, energy identities','terminal Slurm accounting required before capacity signoff'],production_authorized=False,cases=cases,reference_sha256={str(p):sha(p) for p in refs},authority_sha256={str(p.relative_to(R)):sha(p) for p in [R/'manifests/step8_freeze_v1.json',R/'manifests/step9_freeze_v1.json',R/'configs/step6_runtime_authority_v1.json']})
 (R/'manifests/step10_protocol_v1.json').write_text(json.dumps(d,indent=2)+'\n');print('Prepared 21 inputs and three bounded Slurm pilots')
if __name__=='__main__':main()
