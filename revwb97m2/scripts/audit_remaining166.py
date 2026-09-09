"""Independent post-job readback through the unchanged production validator."""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
import numpy as np
from revwb97m2.scripts import generate_training_features_v2 as g


def check_case(task):
    path, name, job = task
    try:
        vector, fixed, differences = g.validate(Path(path), name)
        plan = g.native.read(path)
        case = next(c for c in plan['cases'] if c['species'] == name)
        root = Path(plan['output_root'])/name
        scalar = g.native.read(root/'ready/scalar_values.json')
        if case['electron_count'] == 1:
            g.native.require(scalar['pt2_total_hartree'] == 0, 'one-electron PT2 not zero')
        return dict(species=name, job=job, passed=True, plan_sha256=g.native.digest(path),
            publication_sha256=g.native.digest(root/'species.json'),
            vector_shape=list(vector.shape), finite=bool(np.isfinite(vector).all()),
            grid_shapes={key:list(value.shape) for key,value in differences.items()},
            hf_error_hartree=fixed['pure_hf_reconstruction_error_hartree'],
            pt2_identity_error_hartree=scalar.get('pt2_scaled_identity_error_hartree',0),
            stage_count=len(case['stages']))
    except Exception as error:
        return dict(species=name, job=job, passed=False, error=f'{type(error).__name__}: {error}')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=4)
    args=parser.parse_args()
    g.native.require(not args.output.exists(), 'report exists; preserve historical audit')
    base=g.ROOT/'manifests/production_generator/pilot_remaining_v3'
    tasks=[]
    for memory,job in ((14,'25714429'),(21,'25714430'),(35,'25714431'),(227,'25714463')):
        p=base/f'pilot_remaining_v3_m{memory}.json'
        plan,_=g.load(p)
        g.release_check(p,base/f'pilot_remaining_v3_m{memory}_release_20260908.json')
        tasks.extend((str(p),c['species'],f'{job}_{i}') for i,c in enumerate(plan['cases']))
        print('PASS release/contract:',memory,flush=True)
    records=[]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures=[pool.submit(check_case,t) for t in tasks]
        for future in as_completed(futures):
            record=future.result()
            records.append(record)
            print(len(records), 'PASS' if record['passed'] else 'FAIL',record['species'],record.get('error',''),flush=True)
    records.sort(key=lambda r:r['species'])
    passed=[r for r in records if r['passed']]
    result=dict(passed=len(passed)==166, total=len(records), accepted=len(passed), cases=records,
        total_stages=sum(r['stage_count'] for r in passed),
        max_abs_hf_error_hartree=max((abs(r['hf_error_hartree']) for r in passed),default=None),
        note='New post-job process using existing validator; no runtime changes or native reruns.')
    g.native.write(args.output,result)
    print({k:v for k,v in result.items() if k!='cases'},flush=True)
    if not result['passed']:
        raise SystemExit(1)


if __name__=='__main__':
    main()
