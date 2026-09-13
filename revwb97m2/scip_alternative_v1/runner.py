"""Separate SCIP run/compare/readback CLI; saved Gurobi artifacts are read-only."""
import argparse
import json
import math
from pathlib import Path
import sys
import numpy as np
from .runtime import bootstrap
bootstrap()
from . import backend
from revwb97m2 import production_multistart_v1 as reference

BASE = Path('/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/fitting')


def load_reference(name):
    arrays, ids, settings = reference.load_data()
    if name == 'discovery14':
        release = reference.ROOT / 'revwb97m2/manifests/production_multistart_v1/release_20260911.json'
        _, record, graph, root = reference.check(release)
        reference.check_run_identity(root, release, record)
        task = next(t for t in graph['tasks'] if t['id'] == 'p1_k14_simple_r0')
        rows = np.array([], dtype=int)
        audit = reference.audit_task(task, root, graph, arrays, ids, settings, rows)
        folder, budget = root / task['id'], 14
    elif name == 'selected80':
        root = BASE / 'selective_recovery_v1/25792248'
        validated = reference.reader.validate(root)
        folder, budget = root / 'constrained80', 80
        rows = np.load(folder / 'grid_rows.npy')
        audit = validated[0]
    else:
        raise ValueError('unknown saved reference')
    files = {str(p): reference.c.digest(p) for p in folder.rglob('*') if p.is_file()}
    return arrays, ids, settings, folder, budget, rows, audit, files


def run(output, case, seconds, start_kind, threads, memory_mib):
    if output.resolve() == BASE or BASE not in output.resolve().parents:
        raise ValueError('output must be under the fitting data root')
    if 'scip_alternative_v1' not in output.resolve().parts:
        raise ValueError('output must use separate scip_alternative_v1 directory')
    output.mkdir(parents=True, exist_ok=False)
    arrays, ids, settings, folder, budget, rows, saved_audit, source_hashes = load_reference(case)
    prefix = 'start_' if start_kind == 'original' else ''
    b = np.load(folder / (prefix + 'coefficients.npy'))
    z = np.load(folder / (prefix + 'selection.npy'))
    reference.c.write(output/'reference.json', dict(case=case, folder=str(folder), source_hashes=source_hashes,
        start_kind=start_kind, audit=saved_audit, budget=budget, original_solver_rerun=False))
    np.save(output/'start_coefficients.npy', b)
    np.save(output/'start_selection.npy', z)
    np.save(output/'grid_rows.npy', rows)
    start_audit = reference.v.policy.audit(arrays,b,z,budget,rows,settings,ids)
    reference.c.write(output/'start_audit.json', start_audit)
    m, beta, selected, t, meta = backend.build(arrays,settings,budget,rows,seconds,threads,memory_mib)
    try:
        meta['start_stored'] = backend.assign_start(m,beta,selected,t,arrays,settings,b,z)
        meta['start_note'] = 'stored does not certify feasibility or acceptance during optimization'
        reference.c.write(output/'model.json',meta)
        m.writeProblem(str(output/'model.cip'))
        m.setLogfile(str(output/'scip.log'))
        m.optimize()
        report = dict(status=str(m.getStatus()),runtime=float(m.getSolvingTime()),
            solutions=int(m.getNSols()),nodes=int(m.getNTotalNodes()),passed=False,
            gurobi_used=False,solver='SCIP',objective=None,audit=None)
        if m.getNSols() > 0:
            sol = m.getBestSol()
            coeff = np.array([m.getSolVal(sol,v) for v in beta])
            selection = np.array([m.getSolVal(sol,v) for v in selected])
            np.save(output/'coefficients.npy',coeff)
            np.save(output/'selection.npy',selection)
            audit = reference.v.policy.audit(arrays,coeff,selection,budget,rows,settings,ids)
            exact = audit['audit']['independent']['regularized_objective_hartree2']
            primal,dual = float(m.getObjVal()),float(m.getDualbound())
            report.update(objective=primal,independent_objective=exact,dual_bound=dual,
                gaps=backend.gaps(primal,dual,float(m.getGap())),audit=audit,
                passed=bool(audit['passed'] and math.isclose(primal,exact,rel_tol=1e-7,abs_tol=1e-10)
                            and report['status'] in ('optimal','gaplimit','timelimit')))
        old_result = reference.c.read(folder/'result.json')
        comparison = dict(saved_gurobi_objective=old_result['objective'],
            saved_gurobi_runtime=old_result['runtime'],scip_runtime=report['runtime'],
            scip_independent_objective=report.get('independent_objective'),
            scip_minus_saved_gurobi=None if report.get('independent_objective') is None else
                report['independent_objective']-old_result['objective'],
            caveat='Different solver algorithms/thread use; short SCIP test versus saved longer Gurobi run. '
                   'Incumbent starts are warm-start diagnostics, not a fair cold-start speed comparison.')
        reference.c.require(all(reference.c.digest(Path(n))==sha for n,sha in source_hashes.items()), 'reference changed')
        reference.c.write(output/'result.json',report)
        reference.c.write(output/'comparison.json',comparison)
        reference.publish(output)
        print(json.dumps(dict(case=case,status=report['status'],passed=report['passed'],comparison=comparison)),flush=True)
    finally:
        m.freeProb()
    return report


def validate(output):
    reference.verify_publication(output)
    record = reference.c.read(output/'reference.json')
    arrays,ids,settings,folder,budget,rows,_,hashes = load_reference(record['case'])
    reference.c.require(hashes==record['source_hashes'],'reference identity')
    prefix = 'start_' if record['start_kind']=='original' else ''
    for filename in ('coefficients.npy','selection.npy'):
        reference.c.require(np.array_equal(np.load(output/('start_'+filename)),np.load(folder/(prefix+filename))), 'start identity')
    reference.c.require(np.array_equal(np.load(output/'grid_rows.npy'),rows),'grid identity')
    result=reference.c.read(output/'result.json')
    if result['solutions']:
        actual=reference.v.policy.audit(arrays,np.load(output/'coefficients.npy'),np.load(output/'selection.npy'),
                                        budget,rows,settings,ids)
        reference.reader.compare_report(actual,result['audit'])
        exact=actual['audit']['independent']['regularized_objective_hartree2']
        passed=bool(actual['passed'] and math.isclose(result['objective'],exact,rel_tol=1e-7,abs_tol=1e-10)
                    and result['status'] in ('optimal','gaplimit','timelimit'))
        reference.c.require(passed==result['passed'],'acceptance mismatch')
    else:
        reference.c.require(result['passed'] is False,'no-solution acceptance')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['run','validate'])
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--reference',choices=['discovery14','selected80'],default='discovery14')
    parser.add_argument('--start',choices=['original','incumbent'],default='original')
    parser.add_argument('--seconds',type=float,default=60)
    parser.add_argument('--threads',type=int,default=1)
    parser.add_argument('--memory-mib',type=float,default=8192)
    args=parser.parse_args()
    result=run(args.output,args.reference,args.seconds,args.start,args.threads,args.memory_mib) if args.action=='run' else validate(args.output)
    print('SCIP acceptance:',result['passed'],'Gurobi imported:', 'gurobipy' in sys.modules)
