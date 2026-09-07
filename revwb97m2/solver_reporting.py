"""Strict JSON and explicit raw-versus-derived solver gap reporting."""
import json
import math


def number_state(value):
    if math.isnan(value):
        return 'nan'
    if math.isinf(value):
        return 'positive_infinity' if value > 0 else 'negative_infinity'
    return 'finite'


def gap_report(objective, bound, raw_gap):
    """Never replace the solver's gap with a derived value silently."""
    absolute = abs(objective-bound) if all(map(math.isfinite,(objective,bound))) else math.nan
    relative = (absolute/abs(objective) if objective != 0 else
                (0.0 if absolute == 0 else math.inf)) if math.isfinite(absolute) else math.nan
    consistent = (math.isclose(raw_gap,relative,rel_tol=1e-7,abs_tol=1e-10)
                  if not math.isnan(raw_gap) and not math.isnan(relative) else None)
    return {'gap':raw_gap if math.isfinite(raw_gap) else None,
            'gap_state':number_state(raw_gap),
            'gap_absolute':absolute if math.isfinite(absolute) else None,
            'gap_recomputed':relative if math.isfinite(relative) else None,
            'gap_recomputed_state':number_state(relative),
            'gap_consistent':consistent}


def raw_gap_from_record(record):
    if record['gap'] is not None:
        return record['gap']
    return {'positive_infinity':math.inf,'negative_infinity':-math.inf,
            'nan':math.nan}[record['gap_state']]


def strict_dumps(value):
    # Unexpected nonfinite fields fail loudly rather than corrupt JSON.
    return json.dumps(value,indent=2,allow_nan=False)
