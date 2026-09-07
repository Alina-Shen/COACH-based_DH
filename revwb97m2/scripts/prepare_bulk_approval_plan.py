"""Draft only: deterministic canaries and full remaining fitting-species list."""
import csv
import json
from pathlib import Path
from revwb97m2.qchem_scalar_features import sha256

ROOT=Path(__file__).resolve().parents[1]


def main():
    audit_path=ROOT/'results/production_readiness_20260907.json'
    audit=json.loads(audit_path.read_text())
    inventory={r['species']:r for r in csv.DictReader((ROOT/'manifests/step12/step12_fitting_inventory_v1.csv').open())}
    remaining=[r for r in audit['species'] if r['readiness']!='recorded_reaction_ready_rechecked']
    canaries=[]
    for cls in audit['class_summaries']:
        candidates=[r for r in remaining if r['tier']==cls['tier'] and r['memory_class_mb']==cls['memory_class_mb']]
        chosen=min(candidates,key=lambda r:(int(inventory[r['species']]['orbital_aos']),r['species']))
        canaries.append({'species':chosen['species'],'class_key':cls['class_key'],
                         'resources':{k:chosen[k] for k in ('partition','account','qos','cpus','requested_memory_gib','wall_hours')},
                         'orbital_aos':int(inventory[chosen['species']]['orbital_aos'])})
    report={'status':'draft_for_user_approval_not_executable','submission_authorized':False,
            'audit_sha256':sha256(audit_path),'planned_root':audit['production_root'],
            'scope':'initial 1498 fitting entries / 2799 species only; no final-test data or fitting scan submissions',
            'reuse_candidates':[{'species':r['species'],'artifact':r['reuse_artifact']['artifact']} for r in audit['species'] if r['readiness']=='recorded_reaction_ready_rechecked'],
            'remaining_species':[{k:r[k] for k in ('scope','species','readiness','tier','memory_class_mb','cpus','requested_memory_gib','wall_hours','partition','account','qos','source_record_sha256')} for r in remaining],
            'canaries':canaries,'resource_classes':audit['class_summaries'],
            'stages':[
                'Integrate tested legacy spin scaling, one-electron zero PT2 and field-aware fixed-energy handling in a reusable production reaction-ready driver; regression test before submission.',
                'Revalidate authorities, all candidate reuse paths, disk quota and archive-copy footprint; freeze new production contract and batch manifests.',
                'Seven canaries, one per memory class, serial within each partition and at most two running overall; review all seven before any expansion.',
                'On further approval, remaining mhg work in batches of at most 256 species with shared global concurrency 16; lr8 shared concurrency 1 across both large classes.',
                'Independently validate each completed species and assemble all 1498 fitting entries; do not launch scientific fits automatically.'
            ],
            'global_caps_after_canary_approval':{'mhg_jobs':16,'lr8_jobs':1,'total_jobs':17,'total_cpus':144},
            'retry_policy':'no blind automatic retry; one engineered retry maximum per failed species after cause review and explicit retry approval',
            'stop_conditions':['source/provenance mismatch','corrupt or partial publication','repeated common parser/scaling failure','quota/storage concern','unexpected resource use or unsupported chemistry'],
            'preserve_policy':'read-only authoritative archives; isolated run copies; preserve failures; no automatic deletion or overwriting',
            'limits_not_predictions':True,
            'not_yet_verified':['user/project storage quota and full archive-copy footprint','generalized production driver/reuse migration','live account quotas and resource availability at submission','full-class scalar/fixed-stage runtime calibration']}
    out=ROOT/'results/bulk_generation_approval_plan_20260907.json'
    with out.open('x') as f:
        json.dump(report,f,indent=2,allow_nan=False)
    print(json.dumps({'remaining':len(remaining),'reuse_candidates':len(report['reuse_candidates']),'canaries':canaries,'submission_authorized':False},indent=2))


if __name__=='__main__':
    main()
