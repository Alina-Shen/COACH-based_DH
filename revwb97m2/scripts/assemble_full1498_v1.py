"""Explicit accepted-publication assembly; never runs chemistry or optimization.

Historical pilot acceptance is consumed by hash, not by weakening its frozen
native reader. Full-generation native acceptance is a separate prerequisite.
"""
import argparse
from pathlib import Path
import numpy as np
from revwb97m2 import pilot100_inputs as pilot
from revwb97m2.fit_inputs import ARRAYS, load_inputs
from revwb97m2.scripts import generate_training_features_v3 as g
from revwb97m2.scripts import full_training_feeder_v1 as feeder
from revwb97m2.scripts import prepare_training_preflight as metadata

ROOT = g.ROOT
CAMPAIGN = g.native.DATA.parent/'campaigns/full_training_20260909_v1/campaign.json'
AUDIT = ROOT/'results/2026-09-10-final-generation-audit.json'
PREFLIGHT = ROOT/'results/training_preflight_v2'
GRIDS = ('99590', '75302')
read, digest, require, write = pilot.read, pilot.digest, pilot.require, pilot.write


def checked_metadata():
    checks = read(PREFLIGHT/'checksums.json')
    for name, sha in checks.items():
        require(digest(PREFLIGHT/name) == sha, 'metadata artifact changed')
    audit = read(PREFLIGHT/'audit.json')
    require(audit['metadata_passed'] and not audit['errors'], 'metadata audit failed')
    sources = audit['sources']
    for ref in sources.values():
        require(digest(ref['path']) == ref['sha256'], 'metadata authority changed')
    entries = metadata.rows(sources['entries']['path'])
    dataset = metadata.unique(metadata.rows(sources['dataset']['path']), 'Reaction')
    roles = metadata.unique(metadata.rows(sources['roles']['path']), 'reaction')
    reactions = read(PREFLIGHT/'full1498_reactions.json')
    require(len(entries) == len(reactions) == 1498, 'exact1498 metadata required')
    for index, (entry, reaction) in enumerate(zip(entries, reactions), 1):
        raw, role = dataset[entry['reaction']], roles[entry['reaction']]
        expected = dict(entry, objective_weight=float(entry['objective_weight']),
                        reference_hartree=float(raw['Reference']),
                        stoichiometry=metadata.stoichiometry(raw['Stoichiometry']))
        require(all(reaction[k] == v for k, v in expected.items()), 'source reaction mismatch')
        require(int(entry['global_index']) == index and raw['Dataset'] == entry['dataset_eval_dataset'],
                'source row order/dataset mismatch')
        require(role['coefficient_fitting'] == 'true' and role['final_assessment'] == 'false'
                and float(role['objective_weight']) == reaction['objective_weight'], 'role/weight mismatch')
    return reactions


def collect():
    pilot_arrays, pilot_reactions, settings = pilot.check_matrix()
    accepted = read(pilot.MATRIX/'validation.json')
    authorities = dict(accepted['authorities'])
    for path in (pilot.MATRIX/'validation.json', PREFLIGHT/'checksums.json', AUDIT, CAMPAIGN):
        authorities[str(path)] = digest(path)
    records, sources = {}, {}

    def add(name, root, kind, publication='species.json', ready='ready', fixed=None):
        require(name not in records, 'duplicate source species: '+name)
        root = Path(root)
        pub = read(root/publication)
        files = {str(root/publication): digest(root/publication)}
        for path, sha in pub['artifacts'].items():
            require(digest(root/path) == sha, 'source artifact changed: '+name)
            files[str(root/path)] = sha
        base = root/ready
        paths = [base/'feature_vector_292.npy', *(base/f'grid_difference_{grid}.npy' for grid in GRIDS)]
        if fixed is None:
            paths.append(base/'fixed_energy.json')
        require(all(str(p) in files for p in paths), 'unbound source array/fixed energy')
        records[name] = (np.load(paths[0], allow_pickle=False),
                         read(base/'fixed_energy.json') if fixed is None else fixed,
                         {grid: np.load(base/f'grid_difference_{grid}.npy', allow_pickle=False) for grid in GRIDS})
        sources[name] = dict(kind=kind, root=str(root), artifacts=files,
                             corrected_fixed=fixed)

    base = ROOT/'manifests/production_generator'
    audit_cases = {}
    for filename in ('first16_independent_readback_20260908.json', 'remaining166_independent_readback_20260908.json'):
        report = read(ROOT/'results/pilot_execution_v3'/filename)
        require(report['passed'], 'pilot source audit failed')
        for case in report['cases']:
            require(case['passed'] and case['species'] not in audit_cases, 'duplicate/failed pilot audit')
            audit_cases[case['species']] = dict(case, plan_sha256=case.get('plan_sha256', report.get('plan_sha256')))
    plans = [base/'training_first16_v3.json', *(base/f'pilot_remaining_v3/pilot_remaining_v3_m{m}.json' for m in (14, 21, 35, 227))]
    for path in plans:
        plan = read(path)
        for case in plan['cases']:
            name = case['species']; root = Path(plan['output_root'])/name
            require(digest(path) == audit_cases[name]['plan_sha256'] and
                    digest(root/'species.json') == audit_cases[name]['publication_sha256'], 'pilot acceptance changed')
            add(name, root, 'accepted_pilot_generic')
    legacy = read(ROOT/'results/pilot_execution_v3/legacy38_corrected_audit_20260908.json')
    require(legacy['passed'] and legacy['accepted'] == 38, 'legacy acceptance failed')
    for case in legacy['cases']:
        root = Path(case['vector_path']).parent.parent
        require(case['passed'] and digest(root/'species.json') == case['publication_sha256'] and
                digest(case['vector_path']) == case['vector_sha256'] and
                digest(case['fixed_output']) == case['fixed_output_sha256'], 'legacy correction changed')
        authorities[case['fixed_output']] = case['fixed_output_sha256']
        add(case['species'], root, 'accepted_pilot_explicit_legacy_correction', fixed=case['corrected_fixed'])
    water = read(base/'water_scalar_refresh_v1_base.json')
    add('11_H2O_TA13', Path(water['output_root'])/'11_H2O_TA13', 'accepted_pilot_water', 'water_refresh.json')
    y = read(base/'embedded_y_features_v1.json')
    for case in y['cases']:
        add(case['species'], Path(y['output_root'])/case['species'], 'accepted_pilot_embedded_y')
    canaries = g.corrected.validate_registry()
    registry = read(g.corrected.REGISTRY)
    for name, values in canaries.items():
        # Small checkpoint artifact table lives at its common parent.
        root = Path(registry['species'][name]['root'])
        files = {str(root/p): digest(root/p) for p in ('feature_vector_292.npy', 'fixed_energy.json',
                 'grid_difference_99590.npy', 'grid_difference_75302.npy', 'audit.json')}
        require(name not in records, 'duplicate canary source')
        records[name] = values
        sources[name] = dict(kind='corrected_canary', root=str(root), artifacts=files, corrected_fixed=None)
    require(len(records) == 230, 'exact230 accepted reuse species required')
    require(set(read(pilot.MATRIX/'species.json')) <= set(records), 'pilot species missing')
    print('Accepted pilot/reuse sources PASS: 230', flush=True)
    audit = read(AUDIT); campaign = read(CAMPAIGN)
    require(audit['passed'] and not audit['errors'] and audit['generated_species'] == 2569
            and audit['stages'] == 15412, 'full native audit not accepted')
    require(digest(CAMPAIGN) == audit['controller']['campaign_sha256'], 'audited campaign changed')
    audited = {r['species']: r for r in audit['records']}
    require(len(audited) == len(audit['records']) == 2569 and all(r['passed'] for r in audited.values()),
            'incomplete native acceptance')
    generated = set()
    for record in campaign['records']:
        path = Path(record['plan'])
        require(digest(path) == record['plan_sha256'], 'campaign plan changed')
        plan, _ = g.load(path)
        authorities[str(path)] = digest(path)
        for index, case in enumerate(plan['cases']):
            name = case['species']
            require(audited[name]['plan'] == record['name'], 'audit source group mismatch')
            feeder.publication(record, index)
            add(name, Path(plan['output_root'])/name, 'full_generation')
            generated.add(name)
        print('Publication readback PASS:', record['name'], flush=True)
    require(generated == set(audited), 'native audit coverage mismatch')
    require(set(records)-set(read(pilot.MATRIX/'species.json'))-generated == set(audit['extra_reused_species']),
            'extra canary coverage mismatch')
    for path in (PREFLIGHT/'audit.json', PREFLIGHT/'full1498_reactions.json', Path(__file__),
                 Path(pilot.__file__), ROOT/'reaction_assembly.py', ROOT/'fit_inputs.py'):
        authorities[str(path)] = digest(path)
    return records, sources, authorities, pilot_arrays, pilot_reactions, settings


def assemble_checked(reactions, records, entries=1498, species=2799, groups=49):
    names = sorted({t['species'] for r in reactions for t in r['stoichiometry']})
    require(len(reactions) == entries and len(names) == species and set(names) == set(records),
            'exact entry/species coverage required')
    require(len({r['set_or_subset'] for r in reactions}) == groups, 'wrong group coverage')
    arrays = g.corrected.assemble_with_evidence(reactions, records)
    index = {name: i for i, name in enumerate(names)}
    S = np.zeros((entries, species))
    for i, reaction in enumerate(reactions):
        for term in reaction['stoichiometry']:
            S[i, index[term['species']]] += term['coefficient']
    flat = {k: v for k, v in arrays.items() if isinstance(v, np.ndarray)}
    flat.update({f'grid_difference_{k}': v for k, v in arrays['grid_differences'].items()})
    errors = {}
    channels = dict(feature_matrix=np.stack([records[n][0] for n in names]),
                    fixed_energy=np.array([records[n][1]['fixed_energy_hartree'] for n in names]))
    channels.update({f'grid_difference_{grid}': np.stack([records[n][2][grid] for n in names]) for grid in GRIDS})
    for key, values in channels.items():
        expected = S @ values
        np.testing.assert_allclose(flat[key], expected, rtol=1e-12, atol=2e-10)
        errors[key] = float(np.max(np.abs(flat[key]-expected)))
    require(all(np.isfinite(v).all() for v in flat.values()), 'nonfinite assembled array')
    np.testing.assert_array_equal(flat['objective_weight'], [r['objective_weight'] for r in reactions])
    np.testing.assert_array_equal(flat['reference_energy'], [r['reference_hartree'] for r in reactions])
    np.testing.assert_array_equal(flat['target'], flat['reference_energy']-flat['fixed_energy'])
    require(all(np.all(flat[f'grid_difference_{grid}'][:, 288:] == 0) for grid in GRIDS), 'scalar grid policy changed')
    return flat, names, errors


def check_pilot(flat, reactions, pilot_arrays, pilot_reactions):
    index = {r['reaction']: i for i, r in enumerate(reactions)}
    rows = [index[r['reaction']] for r in pilot_reactions]
    for key, value in pilot_arrays.items():
        np.testing.assert_array_equal(flat[key][rows], value)
    return rows


def validate(output):
    output = Path(output); report = read(output/'validation.json')
    require((output/'MATRIX_COMPLETE').read_text().strip() == digest(output/'validation.json'), 'matrix incomplete')
    require(report['passed'] and (report['entries'], report['species'], report['features']) == (1498, 2799, 292),
            'wrong full matrix validation')
    for path, sha in report['authorities'].items():
        require(digest(path) == sha, 'matrix authority changed')
    for path, sha in report['artifacts'].items():
        require(digest(output/path) == sha, 'matrix artifact changed')
    for source in read(output/'sources.json').values():
        for path, sha in source['artifacts'].items():
            require(digest(path) == sha, 'bound species artifact changed')
    arrays, manifest = load_inputs(output/'inputs.json', g.native.load_fit_settings())
    reactions = checked_metadata()
    require(read(output/'reactions.json') == reactions and manifest['reaction_ids'] == [r['reaction'] for r in reactions],
            'matrix row identity changed')
    arrays.update({k: np.load(output/(k+'.npy'), allow_pickle=False) for k in ('fixed_energy', 'reference_energy')})
    require(all(v.shape == ((1498, 292) if k == 'feature_matrix' or k.startswith('grid_difference') else (1498,))
                and np.isfinite(v).all() for k, v in arrays.items()), 'bad saved array')
    np.testing.assert_array_equal(arrays['reference_energy'], [r['reference_hartree'] for r in reactions])
    np.testing.assert_array_equal(arrays['objective_weight'], [r['objective_weight'] for r in reactions])
    np.testing.assert_array_equal(arrays['target'], arrays['reference_energy']-arrays['fixed_energy'])
    p_arrays, p_reactions, _ = pilot.check_matrix()
    check_pilot(arrays, reactions, p_arrays, p_reactions)
    return report


def publish(output):
    output = Path(output)
    require(not output.exists(), 'preserve existing full matrix')
    reactions = checked_metadata()
    records, sources, authorities, p_arrays, p_reactions, settings = collect()
    flat, names, errors = assemble_checked(reactions, records)
    rows = check_pilot(flat, reactions, p_arrays, p_reactions)
    output.mkdir(parents=True)
    for key, value in flat.items():
        np.save(output/(key+'.npy'), value)
        np.testing.assert_array_equal(np.load(output/(key+'.npy'), allow_pickle=False), value)
    write(output/'reactions.json', reactions); write(output/'species.json', names)
    write(output/'sources.json', sources)
    artifacts = {name: dict(path=name+'.npy', sha256=digest(output/(name+'.npy'))) for name in ARRAYS}
    write(output/'assembly.json', dict(passed=True, scientific_specification_sha256=settings.specification_sha256,
          array_sha256={k: v['sha256'] for k, v in artifacts.items()},
          independent_stoichiometry_max_abs_error=errors, pilot_rows_exact=True,
          sources_sha256=digest(output/'sources.json'), assembly_code_sha256=digest(__file__)))
    artifacts['assembly_validation'] = dict(path='assembly.json', sha256=digest(output/'assembly.json'))
    write(output/'inputs.json', dict(schema_version=1, status='validated', role='coefficient_fitting',
          scientific_specification_sha256=settings.specification_sha256, weights_policy='coach_si_table2_final_cycle',
          reaction_ids=[r['reaction'] for r in reactions], artifacts=artifacts,
          energy_parameters=dict(omega=.3, gamma_ss=.01, vv10_b=5.5, vv10_c=.01),
          vv10_grid_policy='single_grid_zero_difference',
          vv10_grid_zero_reason='VV10 evaluated on SG1 only; zero difference is not a two-grid VV10 stability claim.'))
    loaded, _ = load_inputs(output/'inputs.json', settings)
    for key in ARRAYS:
        np.testing.assert_array_equal(loaded[key], flat[key])
    report = dict(passed=True, entries=1498, species=2799, features=292, groups=49,
                  specification_sha256=settings.specification_sha256, authorities=authorities,
                  independent_stoichiometry_max_abs_error=errors, pilot_rows_exact=True, pilot_row_indices=rows,
                  artifacts={p.name: digest(p) for p in output.iterdir()},
                  scope='Numerical assembly and real fit-input readback only; no optimization or optimality claim.')
    write(output/'validation.json', report)
    (output/'MATRIX_COMPLETE').write_text(digest(output/'validation.json')+'\n')
    return validate(output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('assemble', 'validate'))
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    result = publish(args.output) if args.action == 'assemble' else validate(args.output)
    print('PASS', {k: result[k] for k in ('entries', 'species', 'features', 'pilot_rows_exact', 'independent_stoichiometry_max_abs_error')}, flush=True)
