"""Deterministic frozen two-pass numerical-grid row selection."""
import numpy as np


def select_rows(difference, candidates, per_candidate=100, global_count=200):
    d=np.asarray(difference)
    c=np.asarray(candidates)
    if d.ndim!=2 or c.ndim!=2 or c.shape[1]!=d.shape[1]:
        raise ValueError('grid/candidate dimensions disagree')
    if not np.isfinite(d).all() or not np.isfinite(c).all():
        raise ValueError('nonfinite grid inputs')
    if per_candidate<0 or global_count<0:
        raise ValueError('negative row count')
    indices=set(np.argsort(-np.abs(d).sum(axis=1),kind='stable')[:global_count].tolist())
    for coeff in c:
        indices.update(np.argsort(-np.abs(d@coeff),kind='stable')[:per_candidate].tolist())
    return np.array(sorted(indices),dtype=int)
