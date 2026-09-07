"""Seven fresh v7 resource canaries; historical drivers remain unchanged.

Freeze is explicit and read-only apart from a new manifest. Run preserves every
partial stage and can reuse only completed, hash-validated stages. No submission.
"""
import csv
import json
import re
import shutil
import time
from pathlib import Path

import numpy as np

from revwb97m2.fit_spec import ROOT, load_fit_settings
from revwb97m2.fit_inputs import digest
from revwb97m2.qchem_scalar_features import (
    derive_scalar_input, derive_pt2_input, derive_fixed_energy_input,
    evaluate_d4_atm_from_qchem_input, parse_qchem_fixed_energy_output, tree_manifest,
)
from revwb97m2.step14_recovery_v2 import scalar_values, fixed_energy
from revwb97m2.qchem_feature_publisher import (
    GRID_VALUES, publish_or_resume, validate_published_artifact,
)
from revwb97m2.scripts.prepare_q3_qchem_gateway import derive_input
from revwb97m2.scripts.run_step13_fresh_species import (
    canonical_tree_hash, run_qchem, QCHEM_ROOT, CONTROL_AMENDMENT,
)

INVENTORY = ROOT/'manifests/step12/step12_fitting_inventory_v1.csv'
ORBITALS = Path('/clusterfs/mhg-data/yaoshen/scf_read/wb97m_os_rimp2')
DATA = Path('/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/species')
NAMES = ('TMD01_H', 'S22_06b', 'HR46_N-methylacetamide', 'HR46_toluene',
         '3019_41UracilPentane090_dim_S66x8', 'BSR36_c4', 'MOR16_ed33')
GRIDS = ('250974', '99590', '75302')


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    with Path(path).open('x') as handle:
        json.dump(value, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write('\n')


def electron_count(source):
    """Seven real-atom, all-electron Cartesian canaries only; fail closed."""
    from pyscf.data import elements
    require(not re.search(r'(?im)^\s*\$ecp\b', source), 'ECP canary not supported')
    match = re.search(r'(?ims)^\s*\$molecule\s*\n(.*?)^\s*\$end', source)
    require(match is not None, 'missing molecule')
    lines = [line.split() for line in match[1].splitlines() if line.strip()]
    require(len(lines[0]) == 2, 'invalid charge/multiplicity')
    charge, multiplicity = map(int, lines[0])
    total = -charge
    for row in lines[1:]:
        require(len(row) == 4 and not row[0].startswith('@'), 'unsupported geometry')
        require(np.isfinite([float(x) for x in row[1:]]).all(), 'invalid coordinates')
        total += elements.charge(row[0])
    spin = multiplicity - 1
    require(total > 0 and 0 <= spin <= total and (total-spin) % 2 == 0,
            'invalid electron/spin count')
    return total, spin


def stage_inputs(source, settings):
    inputs = {g: derive_input(source, GRID_VALUES[g],
                             skip_post_fock_diagonalization=True) for g in GRIDS}
    inputs['scalar'] = derive_scalar_input(source, settings=settings)[0]
    inputs['fixed'] = derive_fixed_energy_input(source)[0]
    if electron_count(source)[0] != 1:
        inputs['pt2'] = derive_pt2_input(source)[0]
    return inputs


def code_hashes():
    # Include local transitive scientific dependencies, not only the wrapper.
    paths = list(ROOT.glob('*.py')) + [
        ROOT/'scripts/v7_canary.py', ROOT/'scripts/prepare_q3_qchem_gateway.py',
        ROOT/'scripts/run_step13_fresh_species.py', CONTROL_AMENDMENT,
    ]
    return {str(p.resolve()): digest(p) for p in paths}


def freeze(path, output_root):
    settings = load_fit_settings()
    output_root = Path(output_root).resolve()
    require(output_root.parent == DATA.resolve() and not output_root.exists(),
            'canary output must be a new direct child of species data root')
    rows = {r['species']: r for r in csv.DictReader(INVENTORY.open())}
    cases = []
    for name in NAMES:
        row = rows[name]
        source = Path(row['qchem_input_path'])
        require(digest(source) == row['qchem_input_sha256'], 'input authority changed')
        require(row['has_ecp'] == 'false' and int(row['ghost_atom_count']) == 0,
                'unsupported canary ECP/ghost centers')
        count, spin = electron_count(source.read_text())
        require((count, spin) == (int(row['electron_count']), int(row['spin'])),
                'inventory electron/spin mismatch')
        stage_inputs(source.read_text(), settings)  # Derive only, no calculation.
        orbital = ORBITALS/name
        tree = tree_manifest(orbital)
        require(tree and (orbital/'qarchive.h5').is_file(), 'missing orbital archive')
        cases.append(dict(species=name, authoritative_input=str(source),
                          input_sha256=digest(source), orbital_root=str(orbital),
                          source_record_sha256=row['source_record_sha256'],
                          electron_count=count, spin=spin,
                          source_tree_sha256=canonical_tree_hash(tree),
                          source_tree_bytes=sum(r['bytes'] for r in tree),
                          qarchive_sha256=digest(orbital/'qarchive.h5'),
                          resources={k: int(row[k]) for k in
                                     ('cpus', 'requested_memory_gib', 'wall_hours')},
                          route={k: row[k] for k in ('partition', 'account', 'qos')}))
    build = {str(QCHEM_ROOT/p): digest(QCHEM_ROOT/p) for p in
             ('bin/qchem', 'exe/qcprog.exe', 'lib/libks.so', 'lib/libks_ham.so',
              'lib/libks_ref.so', 'lib/libks_utils.so')}
    write(path, dict(schema_version=1, purpose='seven_fresh_v7_canaries_only',
                     output_root=str(output_root), cases=cases,
                     specification_sha256=settings.specification_sha256,
                     inventory_sha256=digest(INVENTORY), code_hashes=code_hashes(),
                     build_hashes=build, submission_authorized=False,
                     global_two_job_cap=False, large_cases_require_review=True,
                     minimum_copy_bytes=sum(c['source_tree_bytes'] *
                         (5 if c['electron_count'] == 1 else 6) for c in cases),
                     storage_note='copy lower bound only; excludes new Q-Chem scratch and retained failures'))


def load_plan(path):
    plan = read(path)
    settings = load_fit_settings()
    require(plan['schema_version'] == 1 and
            plan['purpose'] == 'seven_fresh_v7_canaries_only', 'unsupported plan')
    require(tuple(c['species'] for c in plan['cases']) == NAMES, 'canary scope changed')
    require(plan['specification_sha256'] == settings.specification_sha256 and
            plan['inventory_sha256'] == digest(INVENTORY), 'science/inventory changed')
    require(plan['code_hashes'] == code_hashes(), 'code identity changed')
    require(all(digest(p) == h for p, h in plan['build_hashes'].items()), 'build changed')
    require(Path(plan['output_root']).resolve().parent == DATA.resolve(), 'unsafe output root')
    return plan, settings


def output_checks(text, count, spin):
    require('Thank you very much for using Q-Chem' in text, 'abnormal Q-Chem termination')
    require(text.count('Reading MOs from coefficient file') >= 2, 'missing saved MOs')
    counts = re.findall(r'There are\s+(\d+) alpha and\s+(\d+) beta electrons', text)
    require(bool(counts), 'missing electron output')
    alpha, beta = map(int, counts[-1])
    require(alpha+beta == count and alpha-beta == spin, 'output electron/spin mismatch')


def validate_stage(root, derived, case, plan_hash):
    record = read(root/'STAGE_COMPLETE.json')
    require(record['plan_sha256'] == plan_hash and record['species'] == case['species'],
            'stale stage identity')
    require(all(digest(root/p) == h for p, h in record['artifacts'].items()),
            'stage artifacts changed')
    require((root/'input.q3.in').read_text() == derived, 'stage input changed')
    require(digest(root/'qcscratch/canary/qarchive.h5') == case['qarchive_sha256'],
            'working qarchive changed')
    output_checks((root/'qchem.out').read_text(), case['electron_count'], case['spin'])


def run_stage(root, name, derived, case, plan_hash, cpus):
    if root.exists():
        validate_stage(root, derived, case, plan_hash)
        return  # Partial stages fail; never silently restart them.
    root.mkdir(parents=True)
    tree = tree_manifest(Path(case['orbital_root']))
    require(canonical_tree_hash(tree) == case['source_tree_sha256'], 'source tree changed')
    scratch = root/'qcscratch/canary'
    shutil.copytree(case['orbital_root'], scratch, copy_function=shutil.copy2)
    require(tree_manifest(scratch) == tree, 'isolated copy mismatch')
    shutil.copy2(case['authoritative_input'], root/'input.authoritative.in')
    (root/'input.q3.in').write_text(derived)
    prepared = dict(species=case['species'], role='coefficient_fitting_canary',
                    grid=name, case_root=str(root.resolve()),
                    source_orbital_root=case['orbital_root'], source_tree=tree,
                    copy_tree=tree, source_copy_tree_identity=True,
                    authoritative_input_sha256=case['input_sha256'],
                    derived_input_sha256=digest(root/'input.q3.in'),
                    mp2_restart_no_scf_required=True,
                    q6_control_amendment=str(CONTROL_AMENDMENT),
                    q6_control_amendment_sha256=digest(CONTROL_AMENDMENT))
    write(root/'PREPARED.json', prepared)
    seconds = run_qchem(root, 'input.q3.in', 'qchem.out', 'canary', cpus, name in GRIDS)
    output_checks((root/'qchem.out').read_text(), case['electron_count'], case['spin'])
    require(digest(scratch/'qarchive.h5') == case['qarchive_sha256'], 'working archive changed')
    require(tree_manifest(Path(case['orbital_root'])) == tree, 'source tree changed during run')
    write(root/'STAGE_COMPLETE.json', dict(species=case['species'], plan_sha256=plan_hash,
          qchem_seconds=seconds, artifacts={p: digest(root/p) for p in
              ('input.authoritative.in', 'input.q3.in', 'qchem.out', 'PREPARED.json')}))


def components(root, case, settings):
    """Reparse raw Q-Chem/Q4 outputs, independent of final serialized vectors."""
    source = Path(case['authoritative_input']).read_text()
    inputs = stage_inputs(source, settings)
    for name, derived in inputs.items():
        validate_stage(root/'stages'/name, derived, case, read(root/'identity.json')['plan_sha256'])
    semilocal = {}
    for g in GRIDS:
        checks, _ = validate_published_artifact(root/'q4'/g, root/'stages'/g)
        require(bool(checks) and all(checks.values()), 'invalid Q4 artifact')
        semilocal[g] = np.load(root/'q4'/g/'semilocal_features_288.npy', allow_pickle=False)
    scalar_text = (root/'stages/scalar/qchem.out').read_text()
    pt2_text = (root/'stages/pt2/qchem.out').read_text() if 'pt2' in inputs else None
    values = scalar_values(scalar_text, pt2_text, one_electron=case['electron_count'] == 1)
    if 'pt2_scaled_identity_error_hartree' in values:
        require(abs(values['pt2_scaled_identity_error_hartree']) <= 5.2e-9,
                'PT2 spin scaling identity failed')
    fixed_text = (root/'stages/fixed/qchem.out').read_text()
    field = bool(re.search(r'(?im)^\s*\$(?:multipole_field|efield)\b', source))
    parser = fixed_energy if field else parse_qchem_fixed_energy_output
    fixed = parser(fixed_text, values['short_range_hf_hartree'])
    require(abs(fixed['pure_hf_reconstruction_error_hartree']) <= 2e-8, 'fixed HF identity failed')
    vector = np.r_[semilocal['250974'], values['short_range_hf_hartree'],
                   values['vv10_hartree'], values['pt2_total_hartree'],
                   evaluate_d4_atm_from_qchem_input(source)]
    require(vector.shape == (292,) and np.isfinite(vector).all(), 'invalid feature vector')
    differences = {g: np.r_[semilocal[g]-semilocal['250974'], np.zeros(4)] for g in GRIDS[1:]}
    return vector, fixed, differences, values


def validate_species(path, species, require_marker=True):
    plan, settings = load_plan(path)
    case = next(c for c in plan['cases'] if c['species'] == species)
    require(digest(case['authoritative_input']) == case['input_sha256'], 'source input changed')
    root = Path(plan['output_root'])/species
    require(read(root/'identity.json') == dict(plan_sha256=digest(path), species=species),
            'species identity mismatch')
    require(not require_marker or (root/'CANARY_COMPLETE').is_file(), 'incomplete canary')
    record = read(root/'species.json')
    require(record['plan_sha256'] == digest(path) and
            record['specification_sha256'] == settings.specification_sha256, 'stale publication')
    require(all(digest(root/p) == h for p, h in record['artifacts'].items()), 'changed publication')
    vector, fixed, differences, values = components(root, case, settings)
    require(np.array_equal(vector, np.load(root/'ready/feature_vector_292.npy')), 'vector readback failed')
    require(read(root/'ready/fixed_energy.json') == fixed, 'fixed readback failed')
    require(read(root/'ready/scalar_values.json') == values, 'scalar readback failed')
    for g, d in differences.items():
        require(np.array_equal(d, np.load(root/f'ready/grid_difference_{g}.npy')), 'grid readback failed')
    return vector, fixed, differences


def run(path, species, cpus, memory_gib, *, large_reviewed=False):
    plan, settings = load_plan(path)
    case = next(c for c in plan['cases'] if c['species'] == species)
    require(species not in NAMES[5:] or large_reviewed,
            'large canaries require explicit post-small-case review')
    require((cpus, memory_gib) == (case['resources']['cpus'], case['resources']['requested_memory_gib']),
            'allocation differs from frozen case')
    require(digest(case['authoritative_input']) == case['input_sha256'], 'source input changed')
    require(canonical_tree_hash(tree_manifest(Path(case['orbital_root']))) == case['source_tree_sha256'],
            'source tree changed before execution')
    root = Path(plan['output_root'])/species
    identity = dict(plan_sha256=digest(path), species=species)
    if root.exists():
        require(read(root/'identity.json') == identity, 'stale species root')
        if (root/'CANARY_COMPLETE').exists():
            validate_species(path, species)
            return
    else:
        root.mkdir(parents=True)
        write(root/'identity.json', identity)
    started = time.monotonic()
    for name, derived in stage_inputs(Path(case['authoritative_input']).read_text(), settings).items():
        run_stage(root/'stages'/name, name, derived, case, digest(path), cpus)
        if name in GRIDS:
            publish_or_resume(root/'stages'/name, root/'q4'/name)
    vector, fixed, differences, values = components(root, case, settings)
    ready = root/'ready'
    ready.mkdir()  # Partial publications are preserved and fail closed.
    np.save(ready/'feature_vector_292.npy', vector)
    for g, d in differences.items():
        np.save(ready/f'grid_difference_{g}.npy', d)
    write(ready/'fixed_energy.json', fixed)
    write(ready/'scalar_values.json', values)
    require(canonical_tree_hash(tree_manifest(Path(case['orbital_root']))) == case['source_tree_sha256'],
            'source tree changed before publication')
    write(root/'species.json', dict(plan_sha256=digest(path),
          specification_sha256=settings.specification_sha256,
          purpose='fresh_seven_canary_not_full_training',
          vv10_grid_zero_reason='SG-1 only; no both-grid VV10 stability claim',
          wall_seconds=time.monotonic()-started,
          artifacts={str(p.relative_to(root)): digest(p) for p in ready.iterdir()}))
    validate_species(path, species, require_marker=False)
    (root/'CANARY_COMPLETE').write_text('complete\n')
