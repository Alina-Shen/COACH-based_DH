from pathlib import Path
import csv,json,hashlib
from check_step2_workbook_reference import read_book
from step3_metrics import evaluate_development
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'manifests/data_roles_v1'
def table(rows):
    header=rows[0];keys={k.rstrip('0123456789'):v for k,v in header.items()}
    return [{keys[k.rstrip('0123456789')]:v for k,v in r.items() if k.rstrip('0123456789') in keys} for r in rows[1:]]
def main():
    bookpath=ROOT.parent/'coach/paper/COACH_raw_data.xlsx';book=read_book(bookpath)
    policy=json.loads((DATA/'policy.json').read_text())
    with (DATA/'reactions.csv').open() as f:reactions=list(csv.DictReader(f))
    needed={r['reaction'] for r in reactions if r['model_selection']=='True'}
    raw=table(book['raw_data']);selected=[r for r in raw if r['Reaction'] in needed]
    assert len(selected)==len(needed) and len({r['Reaction'] for r in selected})==len(needed)
    predictions={r['Reaction']:(float(r['COACH']),float(r['Reference'])) for r in selected}
    result=evaluate_development(policy,reactions,predictions)
    reference={r['Dataset']:float(r['COACH']) for r in table(book['Relative_metric_per_set']) if r['Dataset'] in {d['dataset'] for d in policy['metrics']['datasets']}}
    assert set(reference)==set(result['datasets'])
    errors={d:result['datasets'][d]['ner']-reference[d] for d in reference}
    report=dict(passed=max(map(abs,errors.values()))<1e-8,scope='137 development datasets only; no final-set scoring',
       workbook=str(bookpath),workbook_sha256=hashlib.sha256(bookpath.read_bytes()).hexdigest(),
       maximum_ner_disagreement=max(map(abs,errors.values())),comparison_tolerance=1e-8,ner_differences=errors,result=result)
    (ROOT/'results/step3_metrics_validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS',report['passed'],'max NER diff',report['maximum_ner_disagreement'],'mean',result['overall_mean_ner'])
    print('Largest differences',sorted(errors.items(),key=lambda kv:abs(kv[1]),reverse=True)[:6])
    assert report['passed']
if __name__=='__main__':main()
