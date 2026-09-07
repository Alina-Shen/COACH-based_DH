"""Audit every frozen Step-14 species without publishing or rerunning jobs."""
import csv
import hashlib
import io
import json
import subprocess
from pathlib import Path

import numpy as np

from revwb97m2.qchem_feature_publisher import validate_published_artifact
from revwb97m2.qchem_scalar_features import sha256, tree_manifest, parse_qchem_fixed_energy_output, parse_qchem_scalar_output
from revwb97m2.qchem_step13_stages import BOUNDARY_CONTRACTS, authority_fingerprint, validate_boundary
from revwb97m2.scripts.run_step13_fresh_species import validate_frozen_authorities

ROOT = Path(__file__).resolve().parents[1]


def main():
    contract_path = ROOT / 'manifests/reaction_features/step14_real_reaction_cohort_v1.json'
    contract = json.loads(contract_path.read_text())
    validate_frozen_authorities(contract)
    raw = subprocess.check_output(['sacct', '-j', '25615636', '--starttime', '2026-09-05T23:00:00', '--format=JobID,State,ExitCode,Elapsed,MaxRSS', '-P'], text=True)
    accounting = list(csv.DictReader(io.StringIO(raw), delimiter='|'))
    jobs = {r['JobID']: r for r in accounting}
    reports = []
    for index, case in enumerate(contract['cases']):
        root = Path(contract['run_root']) / case['scope'] / case['species']
        work = root / 'gateway_work'
        records = tree_manifest(Path(case['orbital_root']))
        summary = {'files': len(records), 'bytes': sum(r['bytes'] for r in records), 'manifest_sha256': hashlib.sha256(json.dumps(records, sort_keys=True, separators=(',', ':')).encode()).hexdigest()}
        checks = {
            'terminal_success': jobs[f'25615636_{index}']['State'] == 'COMPLETED' and jobs[f'25615636_{index}']['ExitCode'] == '0:0',
            'source_input_unchanged': sha256(Path(case['authoritative_input'])) == case['authoritative_input_sha256'],
            'source_tree_unchanged': summary == case['source_tree'],
            'fresh_marker': (root / 'FRESH_SPECIES_COMPLETE').is_file(),
            'no_failure_record': not (root / 'FAILURE.json').exists(),
        }
        for grid in ('250974', '99590', '75302'):
            result, _ = validate_published_artifact(work / 'q4' / grid, work / 'grids' / grid)
            checks[f'q4_{grid}'] = bool(result) and all(result.values())
        diagnostic = {}
        ready = root / 'reaction_ready'
        checks['reaction_ready'] = (ready / 'REACTION_READY_COMPLETE').is_file()
        if checks['reaction_ready']:
            manifest = json.loads((ready / 'reaction_ready_manifest.json').read_text())
            checks['ready_identity'] = manifest['species'] == case['species'] and manifest['cohort_contract_sha256'] == sha256(contract_path)
            checks['ready_hashes'] = all(sha256(ready / name) == digest for name, digest in manifest['artifacts_sha256'].items())
            identity = {key: case[key] for key in ('scope', 'species', 'source_record_sha256')}
            authorities = dict(contract['authorities'], fresh_species_contract_sha256=sha256(contract_path))
            fingerprint = authority_fingerprint(identity, authorities)
            for name in BOUNDARY_CONTRACTS:
                checks[f'boundary_{name}'] = validate_boundary(root / name, name, identity, fingerprint)['passed']
            scalar = json.loads((work / 'scalar/published/scalar_manifest.json').read_text())
            parsed = parse_qchem_scalar_output((work / 'scalar/qchem.out').read_text(), (work / 'scalar/qchem.pt2.out').read_text())
            checks['scalar_reparsed'] = all(parsed[k] == scalar['values_hartree'][k] for k in ('short_range_hf_hartree', 'vv10_hartree', 'pt2_total_hartree'))
            fixed = json.loads((ready / 'fixed_energy.json').read_text())
            parsed_fixed = parse_qchem_fixed_energy_output((work / 'fixed_energy/qchem.out').read_text(), parsed['short_range_hf_hartree'])
            checks['fixed_reparsed'] = parsed_fixed == fixed['values'] and all(fixed['checks'].values())
            vector = np.load(ready / 'feature_vector_292.npy')
            checks['vector_finite_shape'] = vector.shape == (292,) and bool(np.isfinite(vector).all())
            checks['vector_exact'] = bool(np.array_equal(vector, np.load(root / 'assembly/feature_vector_292.npy')))
            for grid in ('99590', '75302'):
                expected = np.concatenate((np.load(work / 'q4' / grid / 'semilocal_features_288.npy') - np.load(work / 'q4/250974/semilocal_features_288.npy'), np.zeros(4)))
                checks[f'grid_difference_{grid}'] = bool(np.array_equal(expected, np.load(ready / f'grid_difference_{grid}_minus_250974.npy')))
        else:
            pt2 = (work / 'scalar/qchem.pt2.out').read_text()
            diagnostic = {'normal_pt2_termination': 'Thank you very much for using Q-Chem' in pt2, 'legacy_spin_labels': 'TOTAL SS RI-MP2_ENERGY' in pt2, 'bad_alloc': 'std::bad_alloc' in pt2, 'multipole_field': '$multipole_field' in pt2}
        reports.append({'task': index, 'species': case['species'], 'passed': all(checks.values()), 'checks': checks, 'diagnostic': diagnostic})
        print(index, case['species'], 'PASS' if all(checks.values()) else 'FAIL', flush=True)
    failed = {r['species'] for r in reports if not r['passed']}
    blocked = [r['reaction'] for r in contract['reactions'] if any(t['species'] in failed for t in r['stoichiometry'])]
    report = {'status': 'passed' if not failed else 'failed', 'job_id': 25615636, 'contract_sha256': sha256(contract_path), 'accounting': accounting, 'species': reports, 'passed_species_count': len(reports) - len(failed), 'blocked_reactions': blocked, 'assembly_run': False}
    output = ROOT / 'manifests/reaction_features/step14_terminal_audit_20260906.json'
    with output.open('x') as f:
        json.dump(report, f, indent=2, sort_keys=True)
        f.write('\n')
    print(json.dumps({'output': str(output), 'passed_species': report['passed_species_count'], 'blocked_reactions': blocked}))


if __name__ == '__main__':
    main()
