"""Fresh-process matrix audit using separately accumulated species contributions."""
import argparse
import math
from pathlib import Path
import numpy as np
from revwb97m2.scripts import assemble_full1498_v1 as a


def audit(root):
    root = Path(root)
    report = a.validate(root)
    sources = a.read(root/'sources.json')
    reactions = a.read(root/'reactions.json')
    names = a.read(root/'species.json')
    a.require(sorted(sources) == names == sorted({t['species'] for r in reactions for t in r['stoichiometry']}),
              'source/species closure mismatch')
    values = {}
    for name, source in sources.items():
        base = Path(source['root'])
        if source['kind'] != 'corrected_canary': base = base/'ready'
        fixed = source['corrected_fixed']
        if fixed is None: fixed = a.read(base/'fixed_energy.json')
        values[name] = np.r_[np.load(base/'feature_vector_292.npy', allow_pickle=False),
                            fixed['fixed_energy_hartree'],
                            *(np.load(base/f'grid_difference_{g}.npy', allow_pickle=False) for g in a.GRIDS)]
    # math.fsum is independent of both production vector accumulation and S@X.
    expected = np.array([[math.fsum(float(t['coefficient'])*values[t['species']][j]
                                   for t in r['stoichiometry']) for j in range(877)] for r in reactions])
    channels = {'feature_matrix': expected[:, :292], 'fixed_energy': expected[:, 292],
                'grid_difference_99590': expected[:, 293:585], 'grid_difference_75302': expected[:, 585:]}
    errors = {}
    for key, value in channels.items():
        saved = np.load(root/(key+'.npy'), allow_pickle=False)
        np.testing.assert_allclose(saved, value, rtol=1e-12, atol=2e-10)
        errors[key] = float(np.max(np.abs(saved-value)))
    return dict(passed=True, entries=1498, species=2799, features=292,
                validation_sha256=a.digest(root/'validation.json'), matrix=str(root),
                audit_code_sha256=a.digest(__file__), fsum_max_abs_error=errors,
                pilot_rows_exact=report['pilot_rows_exact'],
                note='Fresh-process bound-source hash checks, independent math.fsum reconstruction and real fit-input loader readback; no fit.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--matrix', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    a.require(not args.report.exists(), 'preserve existing audit')
    result = audit(args.matrix)
    a.write(args.report, result)
    print(result, flush=True)
