"""Versioned corrected seven-case evidence and strict assembly adapter."""
from pathlib import Path
import re
import numpy as np
from revwb97m2.scripts import fixed_energy_checkpoint as checkpoint
from revwb97m2.scripts import run_large_corrected_canaries as large
from revwb97m2.reaction_assembly import assemble_reaction_arrays

v = checkpoint.v
REGISTRY = v.ROOT/'manifests/production_generator/corrected_canary_evidence_v1.json'


def checked_record(path, expected_hash, marker):
    path = Path(path)
    v.require(v.digest(path) == expected_hash, 'evidence record hash changed')
    v.require((path.parent/marker).read_text().strip() == expected_hash, 'evidence marker changed')
    record = v.read(path)
    v.require(record['artifacts'] and all(v.digest(path.parent/p) == h for p, h in record['artifacts'].items()), 'evidence artifacts changed')
    return record


def validate_registry(registry_path=REGISTRY):
    reg = v.read(registry_path)
    v.require(reg['schema_version'] == 1 and set(reg['species']) == set(v.NAMES), 'exact seven evidence entries required')
    v.require(reg['native_plan_sha256'] == v.digest(checkpoint.PLAN), 'native authority changed')
    v.require(reg['large_contract_sha256'] == v.digest(large.CONTRACT), 'large authority changed')
    plan, settings = v.load_plan(checkpoint.PLAN)
    v.require(reg['specification_sha256'] == settings.specification_sha256, 'evidence science changed')
    source = Path(reg['checkpoint_root'])
    saved = checked_record(source/'checkpoint.json', reg['checkpoint_sha256'], 'CHECKPOINT_COMPLETE')
    v.require(saved['passed'] and saved['original_plan_sha256'] == v.digest(checkpoint.PLAN) and
              saved['specification_sha256'] == settings.specification_sha256, 'invalid checkpoint identity')
    v.require(saved['contract_sha256'] == reg['checkpoint_contract_sha256'] and
              v.digest(reg['checkpoint_contract']) == reg['checkpoint_contract_sha256'], 'checkpoint contract changed')
    contract = v.read(reg['checkpoint_contract'])
    v.require(all(v.digest(p) == h for p, h in contract['hashes'].items()), 'checkpoint source changed')
    v.require([c['species'] for c in saved['cases']] == list(v.NAMES[:5]), 'wrong checkpoint cohort')
    result = {}
    for case in plan['cases'][:5]:
        name = case['species']
        ref = reg['species'][name]
        v.require(ref['kind'] == 'corrected_checkpoint' and Path(ref['root']) == source/name, 'wrong small evidence route')
        audit, vector, fixed, differences = checkpoint.audit_case(plan, settings, case)
        root = Path(ref['root'])
        v.require(v.read(root/'audit.json') == audit and v.read(root/'fixed_energy.json') == fixed, 'small evidence readback changed')
        stored = np.load(root/'feature_vector_292.npy', allow_pickle=False)
        checkpoint.compare_vectors(stored, vector)
        for g, d in differences.items():
            v.require(np.array_equal(np.load(root/f'grid_difference_{g}.npy'), d), 'small grid changed')
        result[name] = (stored, fixed, differences)
    large_contract, _, _ = large.load()
    for name in v.NAMES[5:]:
        ref = reg['species'][name]
        root = Path(ref['root'])
        v.require(ref['kind'] == 'corrected_large' and root == Path(large_contract['output_root'])/name, 'wrong large evidence route')
        rec = checked_record(root/'publication.json', ref['publication_sha256'], 'LARGE_CANARY_COMPLETE')
        v.require(rec['species'] == name and rec['contract_sha256'] == reg['large_contract_sha256'], 'wrong large identity')
        large.validate(name)
        result[name] = (np.load(root/'feature_vector_292.npy', allow_pickle=False),
                       v.read(root/'fixed_energy.json'),
                       {g: np.load(root/f'grid_difference_{g}.npy') for g in v.GRIDS[1:]})
    return result


def assemble_with_evidence(reactions, evidence):
    """Accept validated tuples only; base assembly rejects any missing species."""
    return assemble_reaction_arrays(reactions, {n: r[0] for n, r in evidence.items()},
        {n: r[1]['fixed_energy_hartree'] for n, r in evidence.items()},
        {n: r[2] for n, r in evidence.items()}, v.GRIDS[1:])


def components(root, case, settings):
    """Generic postprocessing with corrected final nuclear breakdown for all cases."""
    source = Path(case['authoritative_input']).read_text()
    inputs = v.stage_inputs(source, settings, case['basis_bridge'])
    for name, derived in inputs.items():
        v.validate_stage(root/'stages'/name, derived, case, v.read(root/'identity.json')['plan_sha256'])
    semilocal = {}
    for g in v.GRIDS:
        checks, _ = v.validate_published_artifact(root/'q4'/g, root/'stages'/g)
        v.require(checks and all(checks.values()), 'invalid Q4')
        semilocal[g] = np.load(root/'q4'/g/'semilocal_features_288.npy', allow_pickle=False)
    values = v.scalar_values((root/'stages/scalar/qchem.out').read_text(),
        (root/'stages/pt2/qchem.out').read_text() if 'pt2' in inputs else None,
        one_electron=case['electron_count'] == 1)
    v.require(abs(values.get('pt2_scaled_identity_error_hartree', 0)) <= 5.2e-9, 'PT2 identity failed')
    fixed_text = (root/'stages/fixed/qchem.out').read_text()
    if re.search(r'(?im)^\s*\$(?:multipole_field|efield)\b', source):
        v.require(re.search(r'Nuclear\s+Repu\.\s+Energy\s*=', fixed_text, re.I) is not None,
                  'field case requires final nuclear breakdown')
    fixed = checkpoint.corrected_fixed(fixed_text, values['short_range_hf_hartree'])
    v.require(abs(fixed['pure_hf_reconstruction_error_hartree']) <= 2e-8, 'fixed identity failed')
    vector = np.r_[semilocal['250974'], values['short_range_hf_hartree'], values['vv10_hartree'],
                   values['pt2_total_hartree'], v.evaluate_d4_atm_from_qchem_input(source)]
    v.require(vector.shape == (292,) and np.isfinite(vector).all(), 'invalid vector')
    differences = {g: np.r_[semilocal[g]-semilocal['250974'], np.zeros(4)] for g in v.GRIDS[1:]}
    return vector, fixed, differences, values
