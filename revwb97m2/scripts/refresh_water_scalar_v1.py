"""One native scalar refresh for water; hash-validated semilocal/PT2/fixed reuse."""
import argparse
import os
from pathlib import Path
import subprocess
import numpy as np
from revwb97m2.scripts import generate_training_features_v2 as g
from revwb97m2.scripts.fixed_energy_checkpoint import corrected_fixed

v=g.native
NAME='11_H2O_TA13'
BASE=v.ROOT/'manifests/production_generator/water_scalar_refresh_v1_base.json'
CONTRACT=v.ROOT/'manifests/production_generator/water_scalar_refresh_v1.json'
LAUNCHER=v.ROOT/'slurm/run_water_scalar_refresh_v1.sh'
OLD=Path('/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/step13/fresh_species_v1/gscdb137')/NAME
FIXED=Path('/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/step14/fixed_energy_gateway_v1')/NAME


def reused(case):
    source=Path(case['authoritative_input']).read_text()
    scalar=OLD/'gateway_work/scalar'
    record=v.read(scalar/'published/scalar_manifest.json')
    v.require(all(record['checks'].values()),'legacy scalar checks failed')
    for path,key in ((scalar/'qchem.out','qchem_output_sha256'),(scalar/'qchem.pt2.out','qchem_pt2_output_sha256'),
                     (scalar/'input.step9.in','derived_input_sha256')):
        v.require(v.digest(path)==record['source'][key],'legacy scalar hash changed')
    v.require(record['source']['authoritative_input_sha256']==case['input_sha256'] and
              record['source']['qarchive_sha256']==case['qarchive_sha256'],'legacy source mismatch')
    prepared=v.read(scalar/'PREPARED.json')
    tree=v.tree_manifest(Path(case['orbital_root']))
    v.require(tree==prepared['source_tree']==prepared['copy_tree'],'legacy restart identity mismatch')
    old_values=v.scalar_values((scalar/'qchem.out').read_text(),(scalar/'qchem.pt2.out').read_text())
    dependencies=[scalar/p for p in ('qchem.out','qchem.pt2.out','input.step9.in','PREPARED.json','published/scalar_manifest.json')]
    semilocal={}
    for grid in v.GRIDS:
        q4=OLD/f'gateway_work/q4/{grid}';raw=OLD/f'gateway_work/grids/{grid}'
        checks,_=v.validate_published_artifact(q4,raw)
        v.require(checks and all(checks.values()),'legacy water Q4 failed')
        semilocal[grid]=np.load(q4/'semilocal_features_288.npy')
        dependencies.extend(p for p in q4.iterdir() if p.is_file())
    fixedprep=v.read(FIXED/'PREPARED.json')
    v.require(fixedprep['authoritative_input_sha256']==case['input_sha256'] and
              fixedprep['source_tree']==tree==fixedprep['copy_tree'],'fixed source mismatch')
    v.require(v.digest(FIXED/'input.fixed.in')==fixedprep['derived_input_sha256'],'fixed input changed')
    expected,_=v.derive_fixed_energy_input(source)
    v.require((FIXED/'input.fixed.in').read_text()==expected,'fixed input no longer compatible')
    fixed=corrected_fixed((FIXED/'qchem.out').read_text(),old_values['short_range_hf_hartree'])
    v.require(abs(fixed['pure_hf_reconstruction_error_hartree'])<=2e-8,'fixed identity failed')
    dependencies.extend(FIXED/p for p in ('PREPARED.json','fixed_energy.json','input.fixed.in','qchem.out'))
    vector=np.r_[semilocal['250974'],*[old_values[k] for k in ('short_range_hf_hartree','vv10_hartree','pt2_total_hartree')],
                 v.evaluate_d4_atm_from_qchem_input(source)]
    g.compare_vectors(np.load(OLD/'assembly/feature_vector_292.npy'),vector)
    dependencies.append(OLD/'assembly/feature_vector_292.npy')
    return vector,semilocal,{str(p):v.digest(p) for p in dependencies}


def updated_vector(old, values):
    v.require(abs(values['short_range_hf_hartree']-old[288])<=1e-8,'SR changed beyond approved reuse tolerance')
    v.require(values['pt2_total_hartree']==old[290],'reused PT2 changed')
    new=old.copy();new[289]=values['vv10_hartree']
    v.require(np.isfinite(new).all(),'nonfinite water feature')
    return new


def load():
    plan,settings=g.load(BASE);contract=v.read(CONTRACT)
    v.require(contract['base_plan_sha256']==v.digest(BASE),'base changed')
    v.require(all(v.digest(p)==h for p,h in contract['code_hashes'].items()),'refresh code changed')
    case=plan['cases'][0];v.require(case['species']==NAME and len(plan['cases'])==1,'wrong water scope')
    old,semi,hashes=reused(case)
    v.require(hashes==contract['reuse_hashes'],'water reuse changed')
    return plan,case,old,semi


def validate(require_marker=True):
    plan,case,old,semi=load();root=Path(plan['output_root'])/NAME
    v.require(not require_marker or (root/'WATER_REFRESH_COMPLETE').is_file(),'water refresh incomplete')
    record=v.read(root/'water_refresh.json')
    v.require(record['contract_sha256']==v.digest(CONTRACT),'wrong water publication')
    v.require(all(v.digest(root/p)==h for p,h in record['artifacts'].items()),'water artifact changed')
    v.validate_stage(root/'stages/scalar',case['stages']['scalar']['input'],case,v.digest(BASE))
    values=v.scalar_values((root/'stages/scalar/qchem.out').read_text(),(OLD/'gateway_work/scalar/qchem.pt2.out').read_text())
    new=updated_vector(old,values)
    g.compare_vectors(np.load(root/'ready/feature_vector_292.npy'),new)
    fixed=corrected_fixed((FIXED/'qchem.out').read_text(),old[288])
    v.require(v.read(root/'ready/fixed_energy.json')==fixed,'water fixed mismatch')
    for grid in ('99590','75302'):
        v.require(np.array_equal(np.load(root/f'ready/grid_difference_{grid}.npy'),
                                np.r_[semi[grid]-semi['250974'],np.zeros(4)]),'water grid mismatch')
    return new,fixed


def run(release_path):
    plan,case,old,semi=load()
    release=g.release_check(BASE,release_path)
    v.require(release.get('water_contract_sha256')==v.digest(CONTRACT),'water release contract mismatch')
    contract=v.read(CONTRACT)
    for path,h in {**contract['code_hashes'],str(CONTRACT):v.digest(CONTRACT)}.items():
        relative=str(Path(path).relative_to(v.ROOT.parent))
        import hashlib
        committed=subprocess.check_output(['git','show',release['commit']+':'+relative],cwd=v.ROOT.parent)
        v.require(hashlib.sha256(committed).hexdigest()==h,'uncommitted water refresh')
    route=g.reviewed_routes(plan,release)[NAME]
    for env,key in (('SLURM_JOB_PARTITION','partition'),('SLURM_JOB_ACCOUNT','account'),('SLURM_JOB_QOS','qos')):
        v.require(os.environ.get(env)==route[key],'water route mismatch')
    v.require(int(os.environ['SLURM_CPUS_PER_TASK'])==8 and int(os.environ['SLURM_MEM_PER_NODE'])==14*1024,
              'water allocation mismatch')
    root=Path(plan['output_root'])/NAME
    root.mkdir(parents=True,exist_ok=True)
    import fcntl
    with (root/'execution.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        if (root/'WATER_REFRESH_COMPLETE').exists():
            validate();return
        v.run_stage(root/'stages/scalar','scalar',case['stages']['scalar']['input'],case,v.digest(BASE),8)
        values=v.scalar_values((root/'stages/scalar/qchem.out').read_text(),(OLD/'gateway_work/scalar/qchem.pt2.out').read_text())
        new=updated_vector(old,values)
        fixed=corrected_fixed((FIXED/'qchem.out').read_text(),old[288])
        ready=root/'ready';ready.mkdir(exist_ok=False)
        np.save(ready/'feature_vector_292.npy',new)
        v.write(ready/'fixed_energy.json',fixed)
        for grid in ('99590','75302'):
            np.save(ready/f'grid_difference_{grid}.npy',np.r_[semi[grid]-semi['250974'],np.zeros(4)])
        v.write(root/'water_refresh.json',dict(contract_sha256=v.digest(CONTRACT),
            artifacts={str(p.relative_to(root)):v.digest(p) for p in ready.iterdir()},
            old_vv10_hartree=float(old[289]),new_vv10_hartree=float(new[289]),
            sr_reuse_error_hartree=float(values['short_range_hf_hartree']-old[288])))
        validate(require_marker=False)
        (root/'WATER_REFRESH_COMPLETE').write_text('complete\n')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('freeze','check','run','validate'))
    parser.add_argument('--release',type=Path)
    args=parser.parse_args()
    if args.action=='freeze':
        plan=g.freeze(BASE,[NAME],'water_scalar_refresh_v1')
        old,semi,hashes=reused(plan['cases'][0])
        v.write(CONTRACT,dict(base_plan_sha256=v.digest(BASE),reuse_hashes=hashes,
            code_hashes={str(p):v.digest(p) for p in (Path(__file__),LAUNCHER)},
            native_stages=['scalar'],reused_stages=['250974','99590','75302','pt2','fixed'],
            note='Base plan pins all derived inputs; this contract executes scalar only. Column289 refreshed, other291 unchanged.'))
        print('PASS water reuse and freeze; one scalar stage; no native run')
    elif args.action=='check':
        load();print('PASS water frozen contract and legacy reuse')
    elif args.action=='run':
        run(args.release)
    else:
        validate();print('PASS water refreshed publication')


if __name__=='__main__':
    main()
