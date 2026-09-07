"""Run isolated unit-scale and fixed-energy checks for seven approved cases."""
import argparse
import json
import shutil
import re
from pathlib import Path
import numpy as np
from revwb97m2.qchem_scalar_features import derive_fixed_energy_input, _set_rem, _remove_rem, sha256, tree_manifest, parse_qchem_fixed_energy_output, evaluate_d4_atm_from_qchem_input
from revwb97m2.step14_recovery import scalar_values, legacy_pt2
from revwb97m2.scripts.run_step13_fresh_species import run_qchem

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / 'manifests/reaction_features/step14_recovery_v1.json'


def main():
    args = argparse.ArgumentParser()
    args.add_argument('--index', type=int, required=True)
    index = args.parse_args().index
    contract = json.loads(CONTRACT.read_text())
    for path, digest in contract['code_sha256'].items():
        if sha256(Path(path)) != digest:
            raise ValueError(f'changed code: {path}')
    cohort = json.loads(Path(contract['cohort']).read_text())
    if sha256(Path(contract['cohort'])) != contract['cohort_sha256']:
        raise ValueError('changed cohort')
    case = cohort['cases'][contract['case_indices'][index]]
    species = case['species']
    old = Path(cohort['run_root']) / case['scope'] / species
    output = Path(contract['run_root']) / species
    output.mkdir(parents=True, exist_ok=False)
    source = Path(case['orbital_root'])
    source_tree = tree_manifest(source)
    source_text = Path(case['authoritative_input']).read_text()
    if sha256(Path(case['authoritative_input'])) != case['authoritative_input_sha256'] or sha256(source/'qarchive.h5') != case['qarchive_sha256']:
        raise ValueError('changed source')
    scalar_text = (old/'gateway_work/scalar/qchem.out').read_text()
    one = species == 'W4-17_h'
    values = scalar_values(scalar_text, None if one else (old/'gateway_work/scalar/qchem.pt2.out').read_text(), one_electron=one)
    checks = {}
    for name in (['fixed'] if one else ['unit', 'fixed']):
        work = output / name
        work.mkdir()
        scratch = work/'qcscratch'/name
        shutil.copytree(source, scratch)
        if tree_manifest(scratch) != source_tree:
            raise ValueError('copy differs')
        if name == 'fixed':
            text, _ = derive_fixed_energy_input(source_text)
        else:
            text = (old/'gateway_work/scalar/input.step9.pt2.in').read_text()
            match = re.search(r'(?ims)^\s*\$rem\s*$.*?^\s*\$end\s*$', text)
            rem = _remove_rem(match.group(), 'METHOD')
            rem = _remove_rem(rem, 'DH_PT2_ENGINE')
            for key, value in {'EXCHANGE':'wB97M-V','CORRELATION':'RIMP2','SCS':'3','SSS_FACTOR':'1000000','SOS_FACTOR':'1000000'}.items():
                rem = _set_rem(rem, key, value)
            text = text[:match.start()] + rem + text[match.end():]
        (work/'input.in').write_text(text)
        run_qchem(work, 'input.in', 'qchem.out', name, 8, False)
        checks[f'{name}_archive_unchanged'] = sha256(scratch/'qarchive.h5') == case['qarchive_sha256']
        result_text = (work/'qchem.out').read_text()
        if name == 'unit':
            unit = legacy_pt2(result_text, unit_scaled=True)
            checks['unit_same_spin'] = abs(unit['same_spin']-values['pt2_same_spin_hartree']) <= contract['unit_tolerance_hartree']
            checks['unit_opposite_spin'] = abs(unit['opposite_spin']-values['pt2_opposite_spin_hartree']) <= contract['unit_tolerance_hartree']
            (output/'unit_check.json').write_text(json.dumps({'unit':unit,'recovered':values,'checks':checks}, indent=2)+'\n')
        else:
            fixed = parse_qchem_fixed_energy_output(result_text, values['short_range_hf_hartree'])
            checks['fixed_normal'] = fixed['normal_qchem_termination']
            checks['fixed_reconstruction'] = abs(fixed['pure_hf_reconstruction_error_hartree']) <= 2e-8
            (output/'fixed_energy.json').write_text(json.dumps(fixed, indent=2)+'\n')
    checks['source_tree_unchanged'] = tree_manifest(source) == source_tree
    (output/'validation.json').write_text(json.dumps({'species':species,'checks':checks,'values':values,'contract_sha256':sha256(CONTRACT)}, indent=2)+'\n')
    if not all(checks.values()):
        raise ValueError(f'recovery validation failed: {checks}')
    values['d4_atm_hartree'] = evaluate_d4_atm_from_qchem_input(source_text)
    semilocal = np.load(old/'gateway_work/q4/250974/semilocal_features_288.npy')
    vector = np.concatenate((semilocal, [values[k] for k in ['short_range_hf_hartree','vv10_hartree','pt2_total_hartree','d4_atm_hartree']]))
    np.save(output/'feature_vector_292.npy', vector)
    for grid in ('99590','75302'):
        np.save(output/f'grid_difference_{grid}_minus_250974.npy', np.concatenate((np.load(old/f'gateway_work/q4/{grid}/semilocal_features_288.npy')-semilocal,np.zeros(4))))
    (output/'RECOVERY_COMPLETE').write_text('complete\n')
    print(json.dumps({'species':species,'checks':checks}))


if __name__ == '__main__':
    main()
