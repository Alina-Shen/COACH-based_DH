"""Audit corrected fixed energies for the legacy refresh cohort; no source mutation."""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
import numpy as np
from revwb97m2 import v7_refresh as refresh
from revwb97m2.scripts import fixed_energy_checkpoint as corrected
from revwb97m2.scripts.recover_v7_canary_d4 import compare_vectors

PLAN=refresh.ROOT/'manifests/reaction_features/v7_refresh_plan_v1.json'


def check(name):
    try:
        plan,_=refresh.load_plan(PLAN)
        case=next(c for c in plan['cases'] if c['species']==name)
        vector, old_fixed, differences=refresh.validate_species(PLAN,name)
        refresh.require(refresh.canonical_tree_hash(refresh.tree_manifest(Path(case['orbital_root']))) ==
                        case['source_tree']['manifest_sha256'],'original restart tree changed')
        entry=case['legacy_entry']
        original=Path(refresh.read(refresh.COHORT)['run_root'])/case['scope']/name
        output=Path(entry['artifact'])/'fixed/qchem.out' if entry['recovered'] else \
               original/'gateway_work/fixed_energy/qchem.out'
        fixed=corrected.corrected_fixed(output.read_text(),vector[288])
        refresh.require(abs(fixed['pure_hf_reconstruction_error_hartree'])<=2e-8,'corrected HF identity failed')
        # Re-evaluate geometry-only D4 under current frozen parameters.
        expected=vector.copy()
        expected[291]=corrected.v.evaluate_d4_atm_from_qchem_input(Path(case['authoritative_input']).read_text())
        compare_vectors(vector,expected)
        root=Path(plan['output_root'])/'species'/name
        return dict(species=name,passed=True,vector_path=str(root/'ready/feature_vector_292.npy'),
            vector_sha256=refresh.digest(root/'ready/feature_vector_292.npy'),
            publication_sha256=refresh.digest(root/'species.json'),
            fixed_output=str(output),fixed_output_sha256=refresh.digest(output),
            corrected_fixed=fixed,old_fixed_energy_hartree=old_fixed,
            fixed_delta_hartree=fixed['fixed_energy_hartree']-old_fixed,
            grid_paths={g:str(root/f'ready/grid_difference_{g}.npy') for g in differences},
            unchanged_vector=True)
    except Exception as error:
        return dict(species=name,passed=False,error=f'{type(error).__name__}: {error}')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    refresh.require(not args.output.exists(),'preserve prior report')
    plan,_=refresh.load_plan(PLAN)
    results=[]
    with ProcessPoolExecutor(max_workers=2) as pool:
        for future in as_completed([pool.submit(check,c['species']) for c in plan['cases']]):
            result=future.result();results.append(result)
            print(len(results),'PASS' if result['passed'] else 'FAIL',result['species'],result.get('error',''),flush=True)
    results.sort(key=lambda r:r['species'])
    passed=[r for r in results if r['passed']]
    report=dict(plan_sha256=refresh.digest(PLAN),passed=len(passed)==38,accepted=len(passed),
        cases=results,max_abs_fixed_delta_hartree=max((abs(r['fixed_delta_hartree']) for r in passed),default=None),
        note='Read-only corrected migration audit. Historical vectors/fixed records unchanged; generic v2 reuse route not changed. Water outside refresh cohort remains pending.')
    refresh.write(args.output,report)
    print({k:v for k,v in report.items() if k!='cases'},flush=True)


if __name__=='__main__':
    main()
