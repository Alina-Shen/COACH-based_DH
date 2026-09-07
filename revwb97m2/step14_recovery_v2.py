"""Versioned recovery helpers; original frozen scalar parser stays unchanged."""
import re
import numpy as np
from revwb97m2.qchem_scalar_features import FLOAT, _last_float, parse_qchem_scalar_output


def legacy_pt2(text, *, unit_scaled=False):
    """Read already-scaled legacy spin components using precise coefficients."""
    ss = _last_float(text, (rf'TOTAL\s+SS\s+RI-MP2[ _]ENERGY\s*=\s*({FLOAT})',), 'legacy same-spin')
    os = _last_float(text, (rf'TOTAL\s+OS\s+RI-MP2[ _]ENERGY\s*=\s*({FLOAT})',), 'legacy opposite-spin')
    factors = [1., 1.] if unit_scaled else [
        _last_float(text, (rf'(?m)^\s*a_{spin}\s*=\s*({FLOAT})',), f'a_{spin}')
        for spin in ('ss', 'os')
    ]
    if unit_scaled:
        observed = [_last_float(text, (rf'{spin}\s+Spin\s+Scaling\s+factor\s*=\s*({FLOAT})',), 'unit spin scale') for spin in ('Same','Opposite')]
        if observed != [1., 1.]:
            raise ValueError(f'unit factors not applied: {observed}')
    if not all(np.isfinite(x) and x > 0 for x in factors):
        raise ValueError('invalid spin factors')
    singles = _last_float(text, (rf'non-Brillouin\s+singles\s*=\s*({FLOAT})',), 'singles')
    total = _last_float(text, (rf'Total\s+RIMP2\s+correlation\s+energy\s*=\s*({FLOAT})',), 'legacy total')
    error = total - ss - os - singles
    if abs(error) > 5.2e-9:
        raise ValueError(f'legacy spin/total identity failure: {error}')
    if 'Thank you very much for using Q-Chem' not in text:
        raise ValueError('Q-Chem did not terminate normally')
    return dict(same_spin=ss/factors[0], opposite_spin=os/factors[1],
                total=ss/factors[0]+os/factors[1], factors=factors,
                scaled_sum=ss+os, singles=singles, driver_identity_error=error)


def scalar_values(scalar_text, pt2_text=None, *, one_electron=False):
    """Recover raw scalar values without disguising skipped or stale output."""
    if not one_electron and not re.search(r'TOTAL\s+SS\s+RI-MP2[ _]ENERGY', pt2_text or ''):
        return parse_qchem_scalar_output(scalar_text, pt2_text)
    alpha = _last_float(scalar_text, (rf'Alpha\s+Exchange\s+Energy\s*=\s*({FLOAT})',), 'alpha exchange')
    beta = _last_float(scalar_text, (rf'Beta\s+Exchange\s+Energy\s*=\s*({FLOAT})',), 'beta exchange')
    vv = _last_float(scalar_text, (rf'Nonlocal\s+correlation\s*=\s*({FLOAT})', rf'DFT\s+Correlation\s+Energy\s*=\s*({FLOAT})'), 'VV10')
    if 'Thank you very much for using Q-Chem' not in scalar_text:
        raise ValueError('scalar Q-Chem did not terminate normally')
    if one_electron:
        counts = re.findall(r'There are\s+(\d+) alpha and\s+(\d+) beta electrons', scalar_text)
        if not counts or sum(map(int, counts[-1])) != 1:
            raise ValueError('zero PT2 requires verified one-electron output')
        pt2 = dict(same_spin=0., opposite_spin=0., total=0., reason='one_electron_no_double_excitations')
    else:
        pt2 = legacy_pt2(pt2_text)
        summary = _last_float(pt2_text, (rf'PT2\s+Correlation\s+Energy\s+\(scE_PT2c\)\s*=\s*({FLOAT})',), 'DH summary')
        pt2['summary_minus_scaled_sum'] = summary - pt2['scaled_sum']
    return dict(short_range_hf_hartree=alpha+beta, vv10_hartree=vv,
                pt2_total_hartree=pt2['total'], pt2_same_spin_hartree=pt2['same_spin'],
                pt2_opposite_spin_hartree=pt2['opposite_spin'], recovery_diagnostics=pt2)


def fixed_energy(text, sr_hf):
    """Prefer the final nuclear term, which includes nucleus-field energy."""
    from revwb97m2.qchem_scalar_features import parse_qchem_fixed_energy_output
    result = parse_qchem_fixed_energy_output(text, sr_hf)
    nuclear = _last_float(text, (rf'Nuclear\s+Repu\.\s+Energy\s*=\s*({FLOAT})',), 'final nuclear term')
    delta = nuclear - result['nuclear_repulsion_hartree']
    result['nuclear_repulsion_hartree'] = nuclear
    result['fixed_energy_hartree'] += delta
    result['pure_hf_reconstruction_error_hartree'] += delta
    result['nucleus_field_correction_hartree'] = delta
    return result
