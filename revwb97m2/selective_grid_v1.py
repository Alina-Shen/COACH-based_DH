"""COACH remaining-row selection and selected-only acceptance, version 1.

Historical grid_selection.py and expanded_adapter.py retain their frozen behavior.
"""
import numpy as np
import yaml
from revwb97m2 import expanded_adapter as a

CONFIG = a.c.ROOT / 'revwb97m2/configs/selective_recovery_v1.yaml'


def settings():
    expected = dict(schema_version=1, stage='selective_recovery_v1',
        inherited_overlay='revwb97m2/configs/expanded_validation_v1.yaml',
        row_selection='candidate_union_then_remaining_l1', top_per_candidate=100,
        additional_remaining_l1=200, acceptance='selected_constraints_only',
        full_grid_violations='report_for_user_review', final_model_user_review=True,
        budgets=[80], seconds_per_solve=600, threads=16, bulk_authorized=False)
    a.c.require(yaml.safe_load(CONFIG.read_text()) == expected, 'unsupported selective policy')
    return a.settings()


def select_rows(difference, candidates, per_candidate=100, additional=200):
    d = np.asarray(difference, dtype=float)
    candidates = np.asarray(candidates, dtype=float)
    if (d.ndim != 2 or candidates.ndim != 2 or not len(candidates)
            or candidates.shape[1] != d.shape[1]
            or not np.isfinite(d).all() or not np.isfinite(candidates).all()
            or not isinstance(per_candidate, int) or not isinstance(additional, int)
            or per_candidate < 0 or additional < 0):
        raise ValueError('invalid grid selection inputs')
    # Match the supplied COACH implementation, including its NumPy tie ordering.
    chosen = set()
    for beta in candidates:
        chosen.update(np.argsort(np.abs(d @ beta))[::-1][:per_candidate].tolist())
    remaining = np.asarray(sorted(set(range(len(d))) - chosen), dtype=int)
    if len(remaining) and additional:
        ranked = np.argsort(np.abs(d[remaining]).sum(axis=1))[::-1][:additional]
        chosen.update(remaining[ranked].tolist())
    return np.asarray(sorted(chosen), dtype=int)


def audit(arrays, beta, selected, budget, rows, fit_settings, entry_ids):
    rows = np.asarray(rows)
    n = len(arrays['target'])
    if (len(entry_ids) != n or len(set(entry_ids)) != n or rows.ndim != 1
            or not np.issubdtype(rows.dtype, np.integer) or len(np.unique(rows)) != len(rows)
            or np.any(rows < 0) or np.any(rows >= n)):
        raise ValueError('invalid entry/row identities')
    checked = a.audit(arrays, beta, selected, budget, rows, fit_settings)
    reports = {}
    for grid in ('99590', '75302'):
        values = np.abs(arrays['grid_difference_' + grid] @ beta) * fit_settings.conversion
        bad = np.flatnonzero(values > fit_settings.grid_public_limit * fit_settings.conversion)
        reports[grid] = dict(max_kcal_mol=float(np.max(values, initial=0)),
            count=len(bad), violations=[dict(index=int(i), entry=entry_ids[i],
                absolute_kcal_mol=float(values[i]), selected=bool(i in rows)) for i in bad])
    return dict(passed=checked['passed'], advancement_passed=checked['passed'],
        acceptance_policy='selected_constraints_only', full_grid_passed=checked['full_grid_passed'],
        review_required=bool(reports['99590']['count']), final_model_user_review_required=True,
        audit=checked, grids=reports)
