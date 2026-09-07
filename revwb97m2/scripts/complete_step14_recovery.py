"""Independently validate recovery and assemble the unchanged 20-reaction cohort."""
import csv
import io
import json
import subprocess
from pathlib import Path
import numpy as np
from revwb97m2.qchem_scalar_features import sha256, tree_manifest, parse_qchem_scalar_output, evaluate_d4_atm_from_qchem_input
from revwb97m2.qchem_feature_publisher import validate_published_artifact
from revwb97m2.step14_recovery_v2 import scalar_values, fixed_energy
from revwb97m2.reaction_assembly import assemble_reaction_arrays
from revwb97m2.scripts.run_step13_fresh_species import canonical_tree_hash, validate_frozen_authorities

ROOT = Path(__file__).resolve().parents[1]


def main():
    cohort_path = ROOT/'manifests/reaction_features/step14_real_reaction_cohort_v1.json'
    recovery_path = ROOT/'manifests/reaction_features/step14_recovery_v2.json'
    cohort = json.loads(cohort_path.read_text())
    recovery = json.loads(recovery_path.read_text())
    validate_frozen_authorities(cohort)
    for path,digest in recovery['code_sha256'].items():
        assert sha256(Path(path)) == digest, path
    raw = subprocess.check_output(['sacct','-j','25634381','--format=JobID,State,ExitCode,Elapsed,MaxRSS','-P'], text=True)
    accounting = list(csv.DictReader(io.StringIO(raw), delimiter='|'))
    tasks = {r['JobID']:r for r in accounting}
    assert all(tasks[f'25634381_{i}']['State']=='COMPLETED' and tasks[f'25634381_{i}']['ExitCode']=='0:0' for i in range(7))
    vectors, fixed, differences, evidence = {}, {}, {}, []
    for index,case in enumerate(cohort['cases']):
        name=case['species']
        original=Path(cohort['run_root'])/case['scope']/name
        records=tree_manifest(Path(case['orbital_root']))
        assert canonical_tree_hash(records)==case['source_tree']['manifest_sha256'], name
        assert sha256(Path(case['authoritative_input']))==case['authoritative_input_sha256'], name
        for grid in ('250974','99590','75302'):
            checks,_=validate_published_artifact(original/f'gateway_work/q4/{grid}',original/f'gateway_work/grids/{grid}')
            assert checks and all(checks.values()), (name,grid)
        if index in recovery['case_indices']:
            artifact=Path(recovery['run_root'])/name
            assert (artifact/'RECOVERY_COMPLETE').is_file()
            record=json.loads((artifact/'validation.json').read_text())
            assert record['contract_sha256']==sha256(recovery_path) and all(record['checks'].values())
            scalar_text=(original/'gateway_work/scalar/qchem.out').read_text()
            values=scalar_values(scalar_text,None if index==36 else (original/'gateway_work/scalar/qchem.pt2.out').read_text(),one_electron=index==36)
            assert values==record['values']
            fixed_values=fixed_energy((artifact/'fixed/qchem.out').read_text(),values['short_range_hf_hartree'])
            assert fixed_values==json.loads((artifact/'fixed_energy.json').read_text())
            assert abs(fixed_values['pure_hf_reconstruction_error_hartree'])<=2e-8
            assert sha256(artifact/'fixed/qcscratch/fixed/qarchive.h5')==case['qarchive_sha256']
            # Independent comparison: parse explicit spin lines rather than calling legacy_pt2.
            if index!=36:
                import re
                unit=(artifact/'unit/qchem.out').read_text()
                assert 'The orbitals will not be altered' in unit
                assert '1.0000 wB97M-V' in unit and 'Thank you very much for using Q-Chem' in unit
                for label,key in [('SS','pt2_same_spin_hartree'),('OS','pt2_opposite_spin_hartree')]:
                    value=float(re.findall(r'TOTAL '+label+r' RI-MP2[_ ]ENERGY\s*=\s*([-\d.]+)',unit)[-1])
                    assert abs(value-values[key])<=recovery['unit_tolerance_hartree']
                assert sha256(artifact/'unit/qcscratch/unit/qarchive.h5')==case['qarchive_sha256']
            fixed[name]=fixed_values['fixed_energy_hartree']
        else:
            artifact=original/'reaction_ready'
            manifest=json.loads((artifact/'reaction_ready_manifest.json').read_text())
            assert (artifact/'REACTION_READY_COMPLETE').is_file()
            assert manifest['cohort_contract_sha256']==sha256(cohort_path)
            assert all(sha256(artifact/file)==digest for file,digest in manifest['artifacts_sha256'].items())
            values=parse_qchem_scalar_output((original/'gateway_work/scalar/qchem.out').read_text(),(original/'gateway_work/scalar/qchem.pt2.out').read_text())
            fixed[name]=json.loads((artifact/'fixed_energy.json').read_text())['values']['fixed_energy_hartree']
        vectors[name]=np.load(artifact/'feature_vector_292.npy')
        assert vectors[name].shape==(292,) and np.isfinite(vectors[name]).all()
        assert np.array_equal(vectors[name][:288],np.load(original/'gateway_work/q4/250974/semilocal_features_288.npy'))
        assert np.array_equal(vectors[name][288:291],[values[k] for k in ('short_range_hf_hartree','vv10_hartree','pt2_total_hartree')])
        assert abs(vectors[name][291]-evaluate_d4_atm_from_qchem_input(Path(case['authoritative_input']).read_text()))<=1e-12
        differences[name]={g:np.load(artifact/f'grid_difference_{g}_minus_250974.npy') for g in ('99590','75302')}
        for grid,array in differences[name].items():
            expected=np.concatenate((np.load(original/f'gateway_work/q4/{grid}/semilocal_features_288.npy')-vectors[name][:288],np.zeros(4)))
            assert np.array_equal(array,expected)
        evidence.append({'species':name,'artifact':str(artifact),'vector_sha256':sha256(artifact/'feature_vector_292.npy'),'recovered':index in recovery['case_indices']})
    result=assemble_reaction_arrays(cohort['reactions'],vectors,fixed,differences,['99590','75302'])
    # Independent stoichiometric matrix multiplication verifies all assembly outputs.
    names=[case['species'] for case in cohort['cases']]
    stoich=np.zeros((20,38))
    for i,reaction in enumerate(cohort['reactions']):
        for term in reaction['stoichiometry']:
            stoich[i,names.index(term['species'])]+=term['coefficient']
    assert np.allclose(result['feature_matrix'],stoich@np.stack([vectors[n] for n in names]),rtol=0,atol=1e-12)
    assert np.allclose(result['fixed_energy'],stoich@np.array([fixed[n] for n in names]),rtol=0,atol=1e-12)
    for grid in ('99590','75302'):
        assert np.allclose(result['grid_differences'][grid],stoich@np.stack([differences[n][grid] for n in names]),rtol=0,atol=1e-12)
    assert np.array_equal(result['target'], result['reference_energy']-result['fixed_energy'])
    output=Path(recovery['run_root']).parent/'reactions_recovery_v2'
    assert not output.exists()
    temp=output.with_name('.'+output.name+'.tmp')
    temp.mkdir()
    arrays={k:v for k,v in result.items() if isinstance(v,np.ndarray)}
    arrays.update({f'grid_difference_{k}':v for k,v in result['grid_differences'].items()})
    for key,value in arrays.items():
        np.save(temp/(key+'.npy'),value)
    (temp/'reaction_names.json').write_text(json.dumps(result['reaction_names'],indent=2)+'\n')
    report={'status':'passed','step':14,'reaction_count':20,'species_count':38,'reused_species':31,'recovered_species':7,'cohort_sha256':sha256(cohort_path),'recovery_sha256':sha256(recovery_path),'validator_sha256':sha256(Path(__file__)),'accounting':accounting,'species':evidence,'checks':{'all_species_verified':True,'all_114_grid_sources_verified':True,'independent_stoichiometric_reassembly':True,'target_identity':True},'artifacts_sha256':{p.name:sha256(p) for p in temp.iterdir()},'bulk_submission_authorized':False}
    (temp/'validation.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    (temp/'ASSEMBLY_COMPLETE').write_text('complete\n')
    temp.rename(output)
    with (ROOT/'manifests/reaction_features/step14_recovery_complete_v2.json').open('x') as f:
        json.dump(dict(report,output_root=str(output)),f,indent=2,sort_keys=True)
        f.write('\n')
    print(json.dumps({'status':'passed','output':str(output),'reactions':20,'species':38}))


if __name__=='__main__':
    main()
