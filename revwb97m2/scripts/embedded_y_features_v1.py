"""Bounded embedded-ECP Y/Y+ fixed-orbital generation; preserve successful input blocks."""
import argparse
import csv
import os
from pathlib import Path
import re
import numpy as np
from revwb97m2.scripts import generate_training_features_v2 as g
from revwb97m2.scripts.fixed_energy_checkpoint import corrected_fixed

v=g.native
NAMES=('3d4dIPSS_Y_GS','3d4dIPSS_Y_GS+')
PLAN=v.ROOT/'manifests/production_generator/embedded_y_features_v1.json'
LAUNCHER=v.ROOT/'slurm/run_embedded_y_features_v1.sh'
PRODUCTION=Path('/clusterfs/mhg-data/yaoshen/wb97m_os/GSCDB/wb97m_os_rimp2/work')


def block(source,name):
    matches=re.findall(rf'(?ims)^\s*\${name}\s*\n(.*?)^\s*\$end\b',source)
    v.require(len(matches)==1,'missing/duplicate '+name+' block')
    return matches[0]


def electron_count(source,bridge):
    molecule=block(source,'molecule').split()
    v.require(len(molecule)==6 and molecule[2]=='Y','bounded Y atom geometry required')
    charge,mult=map(int,molecule[:2])
    v.require(bridge['ecp_resolution']=='embedded_qchem_block' and
              bridge['orbital_resolution']=='embedded_qchem_block','embedded basis/ECP bridge required')
    v.require(int(bridge['ecp_electrons'])==28,'unexpected Y core')
    v.require(re.search(r'(?im)^\s*Y-ECP\s+4\s+28\s*$',block(source,'ecp')) is not None,'Y ECP header mismatch')
    for key,value in (('BASIS','GEN'),('ECP','GEN'),('PURECART','11111')):
        v.require(re.search(rf'(?im)^\s*{key}\s+(?:=\s*)?{value}\s*$',block(source,'rem')) is not None,'changed '+key)
    count,spin=39-charge-28,mult-1
    v.require((count,spin) in ((11,1),(10,0)) and
              (count,spin)==(int(bridge['electron_count']),int(bridge['spin'])),'Y valence/spin mismatch')
    return count,spin


def inputs(source,settings,bridge):
    electron_count(source,bridge)
    result={grid:v.derive_input(source,v.GRID_VALUES[grid],skip_post_fock_diagonalization=True) for grid in v.GRIDS}
    result['scalar']=v.derive_scalar_input(source,settings=settings)[0]
    result['fixed']=v.derive_fixed_energy_input(source)[0]
    result['pt2']=v.derive_pt2_input(source)[0]
    for text in result.values():
        for key in ('basis','ecp','molecule'):
            v.require(block(text,key)==block(source,key),'changed authoritative '+key)
        v.require('MP2_RESTART_NO_SCF TRUE' in text,'missing no-SCF control')
    return result


def hashes():
    return {**g.hashes(),**{str(p):v.digest(p) for p in (Path(__file__),LAUNCHER)}}


def freeze():
    settings=v.load_fit_settings()
    inventory={r['species']:r for r in csv.DictReader(v.INVENTORY.open())}
    bridges={r['species']:r for r in csv.DictReader(v.BRIDGE.open())}
    cases=[];references={}
    root=v.DATA/'embedded_y_features_v1';scratch=v.SCRATCH/'embedded_y_features_v1'
    v.require(not root.exists() and not scratch.exists(),'new namespace required')
    for name in NAMES:
        row,bridge=inventory[name],bridges[name]
        source=Path(row['qchem_input_path']);text=source.read_text()
        v.require(v.digest(source)==row['qchem_input_sha256']==v.digest(PRODUCTION/(name+'.in')),
                  'not the successful production input')
        v.require(bridge['qchem_source_input_sha256']==row['qchem_input_sha256'] and
                  bridge['source_record_sha256']==row['source_record_sha256'],'basis bridge identity mismatch')
        count,spin=electron_count(text,bridge)
        output=PRODUCTION/(name+'.out');production=output.read_text()
        alpha,beta=(count+spin)//2,(count-spin)//2
        v.require('Thank you very much for using Q-Chem' in production and
                  re.search(rf'There are\s+{alpha} alpha and\s+{beta} beta electrons',production),
                  'production output lacks expected success/electron evidence')
        references.update({str(p):v.digest(p) for p in (PRODUCTION/(name+'.in'),output)})
        orbital=v.ORBITALS/name;tree=v.tree_manifest(orbital)
        resources={k:int(row[k]) for k in ('cpus','requested_memory_gib','wall_hours')}
        v.require(resources==dict(cpus=8,requested_memory_gib=14,wall_hours=72),'unreviewed Y allocation')
        cases.append(dict(species=name,authoritative_input=str(source),input_sha256=v.digest(source),
            source_record_sha256=row['source_record_sha256'],basis_bridge=bridge,electron_count=count,spin=spin,
            orbital_root=str(orbital),source_tree=tree,source_tree_sha256=v.canonical_tree_hash(tree),
            source_tree_bytes=sum(r['bytes'] for r in tree),qarchive_sha256=v.digest(orbital/'qarchive.h5'),
            scratch_root=str(scratch/name),resources=resources,
            route=dict(partition='cm1',account='lr_qchem',qos='condo_qchem'),
            stages=inputs(text,settings,bridge)))
    build=v.read(g.CANARY)['build_hashes']
    v.require(all(v.digest(p)==h for p,h in build.items()),'build changed')
    v.write(PLAN,dict(schema_version=1,purpose='bounded_embedded_y_fixed_orbitals',cases=cases,
        code_hashes=hashes(),build_hashes=build,production_reference_hashes=references,
        specification_sha256=settings.specification_sha256,inventory_sha256=v.digest(v.INVENTORY),
        basis_bridge_sha256=v.digest(v.BRIDGE),corrected_evidence_sha256=v.digest(g.corrected.REGISTRY),
        output_root=str(root),scratch_root=str(scratch),submission_authorized=False,
        minimum_copy_bytes=sum(c['source_tree_bytes']*6 for c in cases),max_concurrent_jobs=None))


def load():
    plan=v.read(PLAN);settings=v.load_fit_settings()
    v.require(plan['purpose']=='bounded_embedded_y_fixed_orbitals' and
              [c['species'] for c in plan['cases']]==list(NAMES),'wrong Y scope')
    v.require(plan['code_hashes']==hashes() and plan['specification_sha256']==settings.specification_sha256,'code/spec changed')
    v.require(plan['inventory_sha256']==v.digest(v.INVENTORY) and plan['basis_bridge_sha256']==v.digest(v.BRIDGE),'inventory/bridge changed')
    for key in ('build_hashes','production_reference_hashes'):
        v.require(all(v.digest(p)==h for p,h in plan[key].items()),'changed '+key)
    for c in plan['cases']:
        v.require(v.digest(c['authoritative_input'])==c['input_sha256'],'source changed')
        v.require(c['stages']==inputs(Path(c['authoritative_input']).read_text(),settings,c['basis_bridge']),'derived inputs changed')
    return plan,settings


def components(plan,case):
    root=Path(plan['output_root'])/case['species'];semilocal={}
    v.require(v.canonical_tree_hash(v.tree_manifest(Path(case['orbital_root'])))==case['source_tree_sha256'],'restart changed')
    for key,text in case['stages'].items():
        v.validate_stage(root/'stages'/key,text,case,v.digest(PLAN))
    for grid in v.GRIDS:
        checks,_=v.validate_published_artifact(root/'q4'/grid,root/'stages'/grid)
        v.require(checks and all(checks.values()),'Y Q4 failed')
        semilocal[grid]=np.load(root/f'q4/{grid}/semilocal_features_288.npy')
    values=v.scalar_values((root/'stages/scalar/qchem.out').read_text(),(root/'stages/pt2/qchem.out').read_text())
    v.require(abs(values.get('pt2_scaled_identity_error_hartree',0))<=5.2e-9,'PT2 identity failed')
    fixed=corrected_fixed((root/'stages/fixed/qchem.out').read_text(),values['short_range_hf_hartree'])
    v.require(abs(fixed['pure_hf_reconstruction_error_hartree'])<=2e-8,'Y fixed identity failed')
    vector=np.r_[semilocal['250974'],*[values[k] for k in ('short_range_hf_hartree','vv10_hartree','pt2_total_hartree')],
                 v.evaluate_d4_atm_from_qchem_input(Path(case['authoritative_input']).read_text())]
    v.require(vector.shape==(292,) and np.isfinite(vector).all(),'invalid Y vector')
    return vector,fixed,{grid:np.r_[semilocal[grid]-semilocal['250974'],np.zeros(4)] for grid in ('99590','75302')}


def validate(name,require_marker=True):
    plan,_=load();case=next(c for c in plan['cases'] if c['species']==name);root=Path(plan['output_root'])/name
    v.require(not require_marker or (root/'GENERATION_COMPLETE').is_file(),'incomplete Y publication')
    record=v.read(root/'species.json')
    v.require(record['plan_sha256']==v.digest(PLAN) and all(v.digest(root/p)==h for p,h in record['artifacts'].items()),'Y publication changed')
    vector,fixed,differences=components(plan,case)
    g.compare_vectors(np.load(root/'ready/feature_vector_292.npy'),vector)
    v.require(v.read(root/'ready/fixed_energy.json')==fixed,'Y fixed readback changed')
    for grid,value in differences.items():
        v.require(np.array_equal(np.load(root/f'ready/grid_difference_{grid}.npy'),value),'Y grid changed')
    return vector,fixed,differences


def run(index,release):
    plan,_=load();approved=g.release_check(PLAN,release)
    v.require(index in (0,1),'invalid Y index');case=plan['cases'][index];name=case['species']
    route=g.reviewed_routes(plan,approved)[name]
    for env,key in (('SLURM_JOB_PARTITION','partition'),('SLURM_JOB_ACCOUNT','account'),('SLURM_JOB_QOS','qos')):
        v.require(os.environ.get(env)==route[key],'Y scheduler route mismatch')
    v.require(int(os.environ['SLURM_CPUS_PER_TASK'])==8 and int(os.environ['SLURM_MEM_PER_NODE'])==14*1024,'Y allocation mismatch')
    v.require(v.available_bytes(plan['output_root'])>plan['minimum_copy_bytes']+14*1024**3,'insufficient space')
    root=Path(plan['output_root'])/name;root.mkdir(parents=True,exist_ok=True)
    import fcntl
    with (root/'execution.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        if (root/'GENERATION_COMPLETE').exists():
            validate(name);return
        for key,text in case['stages'].items():
            v.run_stage(root/'stages'/key,key,text,case,v.digest(PLAN),8)
            if key in v.GRIDS:v.publish_or_resume(root/'stages'/key,root/'q4'/key)
        vector,fixed,differences=components(plan,case)
        ready=root/'ready';ready.mkdir(exist_ok=False)
        np.save(ready/'feature_vector_292.npy',vector);v.write(ready/'fixed_energy.json',fixed)
        for key,value in differences.items():np.save(ready/f'grid_difference_{key}.npy',value)
        v.write(root/'species.json',dict(plan_sha256=v.digest(PLAN),species=name,
            artifacts={str(p.relative_to(root)):v.digest(p) for p in ready.iterdir()}))
        validate(name,require_marker=False)
        (root/'GENERATION_COMPLETE').write_text('complete\n')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('freeze','check','run','validate'))
    parser.add_argument('--index',type=int);parser.add_argument('--release',type=Path)
    args=parser.parse_args()
    if args.action=='freeze':freeze();print('PASS frozen Y pair; no native execution')
    elif args.action=='check':load();print('PASS embedded Y contract and preserved inputs')
    elif args.action=='run':run(args.index,args.release)
    else:validate(NAMES[args.index]);print('PASS Y readback')


if __name__=='__main__':main()
