"""Hash-checked v7 reaction data; old b=10 pilot arrays are not implicit inputs."""
from pathlib import Path
import hashlib
import json
import numpy as np

ARRAYS = ('feature_matrix', 'target', 'objective_weight', 'grid_difference_99590',
          'grid_difference_75302')


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for block in iter(lambda: handle.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def load_inputs(manifest_path, settings):
    path = Path(manifest_path).resolve()
    manifest = json.loads(path.read_text())
    if (manifest.get('schema_version') != 1 or manifest.get('status') != 'validated' or
        manifest.get('scientific_specification_sha256') != settings.specification_sha256 or
        manifest.get('energy_parameters') != {'omega': 0.3, 'gamma_ss': 0.01, 'vv10_b': 5.5, 'vv10_c': 0.01} or
        manifest.get('role') != 'coefficient_fitting'):
        raise ValueError('stale, invalid or wrong-role v7 data manifest')
    if manifest.get('weights_policy') != 'coach_si_table2_final_cycle':
        raise ValueError('incorrect training-weight policy')
    records = manifest['artifacts']
    arrays = {}
    for name in ARRAYS:
        record = records[name]
        source = (path.parent / record['path']).resolve()
        if digest(source) != record['sha256']:
            raise ValueError(f'changed {name}')
        arrays[name] = np.load(source, allow_pickle=False)
    a = arrays['feature_matrix']
    n = len(a)
    if n < 1 or a.shape != (n, 292):
        raise ValueError('invalid feature matrix')
    for name in ARRAYS:
        shape = (n,) if name in ('target', 'objective_weight') else (n,292)
        if arrays[name].shape != shape or not np.isfinite(arrays[name]).all():
            raise ValueError(f'invalid {name}')
    if np.any(arrays['objective_weight'] <= 0):
        raise ValueError('nonpositive weights')
    rows = manifest['reaction_ids']
    if len(rows) != n or len(set(rows)) != n:
        raise ValueError('reaction identities mismatch')
    for name in ('grid_difference_99590', 'grid_difference_75302'):
        if np.any(arrays[name][:, [288,290,291]] != 0):
            raise ValueError('grid-independent scalar difference is nonzero')
    if manifest.get('vv10_grid_policy') != 'single_grid_zero_difference':
        raise ValueError('unsupported VV10 grid policy')
    if not manifest.get('vv10_grid_zero_reason') or any(
        np.any(arrays[name][:,289] != 0) for name in ('grid_difference_99590','grid_difference_75302')):
        raise ValueError('missing VV10 zero-difference provenance')
    # A separate assembly validator must publish and hash this evidence. Merely
    # placing the old arrays beside a new manifest is not sufficient provenance.
    evidence = records['assembly_validation']
    evidence_path = (path.parent / evidence['path']).resolve()
    if digest(evidence_path) != evidence['sha256']:
        raise ValueError('changed assembly validation')
    validation = json.loads(evidence_path.read_text())
    if (validation.get('passed') is not True or
        validation.get('scientific_specification_sha256') != settings.specification_sha256 or
        validation.get('array_sha256') != {name:records[name]['sha256'] for name in ARRAYS}):
        raise ValueError('assembly evidence does not validate these v7 arrays')
    return arrays, manifest
