"""Versioned strict adapter for the accepted100-entry numerical matrix."""
import json
from pathlib import Path
import numpy as np
from .fit_inputs import ARRAYS, digest, load_inputs
from .fit_spec import load_fit_settings

ROOT = Path(__file__).resolve().parent.parent
MATRIX = Path('/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/matrices/pilot100_v1')
VALIDATION_SHA = '4e22fc55ed9c78609865463c5e08fdef0283abc07d07112dfb508b3fe4791f18'
REACTIONS = ROOT/'revwb97m2/results/training_preflight_v2/pilot100_reactions.json'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    with Path(path).open('x') as handle:
        handle.write(json.dumps(value, indent=2, allow_nan=False)+'\n')


def check_matrix(root=MATRIX, expected=VALIDATION_SHA, reactions_path=REACTIONS):
    root=Path(root); settings=load_fit_settings()
    require(digest(root/'validation.json')==expected, 'matrix validation changed')
    require((root/'MATRIX_COMPLETE').read_text().strip()==expected, 'matrix incomplete')
    record=read(root/'validation.json')
    require(record['passed'] is True and record['specification_sha256']==settings.specification_sha256,
            'matrix scientific identity mismatch')
    required={k+'.npy' for k in (*ARRAYS,'reference_energy','fixed_energy')}|{'reactions.json','species.json'}
    require(required<=set(record['artifacts']), 'matrix artifacts incomplete')
    require(all(digest(root/p)==h for p,h in record['artifacts'].items()), 'matrix artifact changed')
    require(all(digest(p)==h for p,h in record['authorities'].items()), 'matrix authority changed')
    require(digest(ROOT/'revwb97m2/scripts/assemble_pilot100_v1.py')==record['code_sha256'], 'assembly code changed')
    reactions=read(root/'reactions.json')
    require(digest(reactions_path)==record['source_reactions_sha256'] and reactions==read(reactions_path),
            'reaction metadata changed')
    species={t['species'] for r in reactions for t in r['stoichiometry']}
    require(len(reactions)==100 and len(species)==224 and sorted(species)==read(root/'species.json'),
            'wrong pilot scope')
    require(len({r['reaction'] for r in reactions})==100 and len({r['set_or_subset'] for r in reactions})==49,
            'wrong reaction identities/groups')
    arrays={name:np.load(root/(name+'.npy'),allow_pickle=False) for name in (*ARRAYS,'reference_energy','fixed_energy')}
    for name,value in arrays.items():
        shape=(100,292) if name=='feature_matrix' or name.startswith('grid_difference') else (100,)
        require(value.shape==shape and np.isfinite(value).all(), 'invalid matrix array')
    np.testing.assert_array_equal(arrays['objective_weight'],[r['objective_weight'] for r in reactions])
    np.testing.assert_array_equal(arrays['reference_energy'],[r['reference_hartree'] for r in reactions])
    np.testing.assert_array_equal(arrays['target'],arrays['reference_energy']-arrays['fixed_energy'])
    return arrays,reactions,settings


def publish(output):
    output=Path(output)
    require(not output.exists(), 'preserve existing adapter')
    arrays,reactions,settings=check_matrix()
    output.mkdir(parents=True)
    artifacts={name:dict(path=str(MATRIX/(name+'.npy')),sha256=digest(MATRIX/(name+'.npy'))) for name in ARRAYS}
    evidence=dict(passed=True,scientific_specification_sha256=settings.specification_sha256,
        array_sha256={k:v['sha256'] for k,v in artifacts.items()},
        numerical_validation_sha256=VALIDATION_SHA,numerical_validation_path=str(MATRIX/'validation.json'),
        adapter_code_sha256=digest(__file__),purpose='exact100_validated_matrix_adapter')
    write(output/'assembly.json',evidence)
    artifacts['assembly_validation']=dict(path='assembly.json',sha256=digest(output/'assembly.json'))
    manifest=dict(schema_version=1,status='validated',role='coefficient_fitting',
        scientific_specification_sha256=settings.specification_sha256,
        weights_policy='coach_si_table2_final_cycle',reaction_ids=[r['reaction'] for r in reactions],
        energy_parameters=dict(omega=.3,gamma_ss=.01,vv10_b=5.5,vv10_c=.01),
        vv10_grid_policy='single_grid_zero_difference',
        vv10_grid_zero_reason='VV10 evaluated on SG1 only; zero difference is not a two-grid VV10 stability claim.',
        artifacts=artifacts,numerical_validation_sha256=VALIDATION_SHA)
    write(output/'inputs.json',manifest)
    loaded,_=load_inputs(output/'inputs.json',settings)
    for key in ARRAYS:
        np.testing.assert_array_equal(loaded[key],arrays[key])
    write(output/'publication.json',dict(artifacts={p.name:digest(p) for p in output.iterdir()}))
    (output/'ADAPTER_COMPLETE').write_text(digest(output/'publication.json')+'\n')
    return output/'inputs.json'


def validate(output):
    output=Path(output); arrays,reactions,settings=check_matrix()
    require((output/'ADAPTER_COMPLETE').read_text().strip()==digest(output/'publication.json'), 'adapter incomplete')
    record=read(output/'publication.json')
    require(set(record['artifacts'])=={'assembly.json','inputs.json'}, 'adapter artifact set changed')
    require(all(digest(output/p)==h for p,h in record['artifacts'].items()), 'adapter changed')
    evidence=read(output/'assembly.json')
    require(evidence['numerical_validation_sha256']==VALIDATION_SHA and evidence['adapter_code_sha256']==digest(__file__),
            'adapter authority changed')
    loaded,manifest=load_inputs(output/'inputs.json',settings)
    require(manifest['reaction_ids']==[r['reaction'] for r in reactions], 'adapter rows changed')
    for key in ARRAYS:
        np.testing.assert_array_equal(loaded[key],arrays[key])
    return output/'inputs.json'
