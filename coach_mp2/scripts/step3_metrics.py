"""Solver-neutral metrics for already transformed benchmark property values."""
import math

def dataset_metric(rule, records):
    """records: ordered (reaction_id, calculated, reference) in reporting units."""
    if not records or len({r[0] for r in records})!=len(records):raise ValueError('Empty or duplicate rows')
    if not all(math.isfinite(x) for r in records for x in r[1:]):raise ValueError('Nonfinite values')
    errors=[a-b for _,a,b in records];kind=rule['kind']
    if kind=='MAE':value=math.fsum(map(abs,errors))/len(errors)
    elif kind=='MARE':
        if any(b==0 for _,_,b in records):raise ValueError('Zero relative-error reference')
        value=math.fsum(abs((a-b)/b) for _,a,b in records)/len(records)
    elif kind=='regularized_MAE':value=math.fsum(abs(a-b)/max(abs(b),1.) for _,a,b in records)/len(records)
    elif kind=='weighted_absolute_sum':
        if {r[0] for r in records}!=set(rule['weights']):raise ValueError('Weighted metric membership mismatch')
        value=math.fsum(abs(a-b)*rule['weights'][name] for name,a,b in records)+rule['offset']
    else:raise ValueError('Unknown metric')
    standard=rule['standard_metric']
    if not math.isfinite(standard) or standard<=0:raise ValueError('Invalid normalization')
    return value,value/standard

def evaluate_development(policy, reactions, predictions):
    """Never reads final-only predictions: development rows must match exactly."""
    expected=[r for r in reactions if r['model_selection'] in (True,'True','true')]
    ids={r['reaction'] for r in expected}
    if set(predictions)!=ids:raise ValueError('Require exact development membership; missing/extra/final rows forbidden')
    groups={}
    for row in expected:
        a,b=predictions[row['reaction']]
        groups.setdefault(row['dataset'],[]).append((row['reaction'],a,b))
    rules=policy['metrics']['datasets']
    if set(groups)!={r['dataset'] for r in rules}:raise ValueError('Dataset coverage mismatch')
    metrics={};categories={}
    for rule in rules:
        metric,ner=dataset_metric(rule,groups[rule['dataset']]);metrics[rule['dataset']]={'metric':metric,'ner':ner}
        categories.setdefault(rule['category'],[]).append(ner)
    return dict(datasets=metrics,overall_mean_ner=math.fsum(v['ner'] for v in metrics.values())/len(metrics),
                category_mean_ner={k:math.fsum(v)/len(v) for k,v in categories.items()},
                overfitting_mean_ner=math.fsum(metrics[k]['ner'] for k in ['AE11','MB08-165','MB16-43'])/3)
