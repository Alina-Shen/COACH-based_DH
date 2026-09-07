"""Non-submitting inventory of fitting feature artifacts and reusable evidence."""
import csv
import json
import subprocess
from collections import Counter
from pathlib import Path
import numpy as np
from revwb97m2.qchem_scalar_features import sha256

ROOT=Path(__file__).resolve().parents[1]
DATA=Path('/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2')


def main():
    plan_path=ROOT/'manifests/production_generator/step13_qchem_initial_plan_v3.json'
    plan=json.loads(plan_path.read_text())
    inventory={r['species']:r for r in plan['species']}
    assert len(inventory)==2799
    assert sha256(ROOT.parent/plan['inventory'])==plan['inventory_sha256']
    files=subprocess.check_output(['rg','--files',str(DATA)],text=True).splitlines()
    candidates={name:[] for name in inventory}
    file_counts=Counter()
    for filename in files:
        p=Path(filename)
        if p.name not in ('feature_vector_292.npy','semilocal_features_288.npy','scalar_manifest.json','fixed_energy.json'):
            continue
        file_counts[p.name]+=1
        matches=set(p.parts)&inventory.keys()
        for name in matches:
            candidates[name].append(filename)
    complete_path=ROOT/'manifests/reaction_features/step14_recovery_complete_v2.json'
    complete=json.loads(complete_path.read_text())
    cohort=json.loads((ROOT/'manifests/reaction_features/step14_real_reaction_cohort_v1.json').read_text())
    cases={r['species']:r for r in cohort['cases']}
    ready={}
    for record in complete['species']:
        name=record['species']; p=Path(record['artifact']); case=cases[name]
        original=Path(cohort['run_root'])/case['scope']/name
        v=np.load(p/'feature_vector_292.npy')
        checks={'inventory_identity':name in inventory and inventory[name]['source_record_sha256']==case['source_record_sha256'],
                'vector_hash':sha256(p/'feature_vector_292.npy')==record['vector_sha256'],
                'vector_shape_finite':v.shape==(292,) and bool(np.isfinite(v).all()),
                'input_hash':sha256(Path(case['authoritative_input']))==case['authoritative_input_sha256'],
                'fixed_present':(p/'fixed_energy.json').is_file()}
        if record['recovered']:
            rec=json.loads((p/'validation.json').read_text())
            checks['completion']=(p/'RECOVERY_COMPLETE').is_file() and all(rec['checks'].values())
        else:
            rec=json.loads((p/'reaction_ready_manifest.json').read_text())
            checks['completion']=(p/'REACTION_READY_COMPLETE').is_file() and all(sha256(p/f)==h for f,h in rec['artifacts_sha256'].items())
        checks['semilocal_prefix']=np.array_equal(v[:288],np.load(original/'gateway_work/q4/250974/semilocal_features_288.npy'))
        for grid in ('99590','75302'):
            difference=np.load(p/f'grid_difference_{grid}_minus_250974.npy')
            expected=np.r_[np.load(original/f'gateway_work/q4/{grid}/semilocal_features_288.npy')-v[:288],np.zeros(4)]
            checks[f'difference_{grid}']=np.array_equal(difference,expected)
        ready[name]={'artifact':str(p),'checks':{k:bool(v) for k,v in checks.items()},
                     'passed':all(checks.values()),'vector_sha256':record['vector_sha256']}
    usable={n for n,r in ready.items() if r['passed']}
    entries=list(csv.DictReader((ROOT/'manifests/weights/coach_si_table2_final_cycle_entries.csv').open()))
    metadata={r['Reaction']:r for r in csv.DictReader((ROOT/'manifests/gscdb137/source/DatasetEval.csv').open())}
    reactions=[]
    for entry in entries:
        fields=metadata[entry['reaction']]['Stoichiometry'].split(',')
        names=set(fields[1::2])
        reactions.append({'global_index':entry['global_index'],'reaction':entry['reaction'],
                          'missing_species':sorted(names-usable)})
    species=[]
    for name,row in inventory.items():
        species.append(dict(row,artifact_candidates=candidates[name],
                            readiness='recorded_reaction_ready_rechecked' if name in usable else
                            'partial_or_unvalidated_candidates' if candidates[name] else 'no_feature_candidates',
                            reuse_artifact=ready.get(name)))
    classes=[]
    for cls in plan['class_summaries']:
        group=[r for r in species if r['tier']==cls['tier'] and r['memory_class_mb']==cls['memory_class_mb']]
        classes.append(dict(cls,reuse_count=sum(r['species'] in usable for r in group),
                            remaining_count=sum(r['species'] not in usable for r in group)))
    reaction_root=Path(complete['output_root'])
    report={'submission_authorized':False,'scan_root':str(DATA),
            'scope_note':'File inventory excludes paths outside this project data root; candidates are not automatically validated. Recorded Step14 hashes rechecked; full orbital/source revalidation remains required before reuse publication.',
            'authorities':{str(p):sha256(p) for p in (plan_path,complete_path)},
            'production_root':plan['production_root'],'production_root_exists':Path(plan['production_root']).exists(),
            'counts':dict(Counter(r['readiness'] for r in species)),
            'candidate_file_counts':dict(file_counts),'training_entries':len(entries),
            'entries_with_all_species_ready':sum(not r['missing_species'] for r in reactions),
            'existing_20_reaction_array_hashes_pass':all(sha256(reaction_root/f)==h for f,h in complete['artifacts_sha256'].items()),
            'class_summaries':classes,'species':species,'reactions':reactions}
    out=ROOT/'results/production_readiness_20260907.json'
    with out.open('x') as f:
        json.dump(report,f,indent=2,allow_nan=False)
    print(json.dumps({k:report[k] for k in ('counts','candidate_file_counts','training_entries','entries_with_all_species_ready','existing_20_reaction_array_hashes_pass','production_root_exists','class_summaries')},indent=2))


if __name__=='__main__':
    main()
