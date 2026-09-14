"""Bounded test-only solve/readback; never relax the frozen production reader."""
import numpy as np


def values(variables):
    return np.array([variables[j].X for j in range(292)])


def solve(old, task, root, graph, arrays, ids, settings, rows, env):
    if task['seconds'] != 120: raise ValueError('smoke budget must be120seconds')
    folder=root/task['id']; folder.mkdir()
    original,b,z,diagnostic=old.start_inputs(task,root,graph,arrays,ids,settings,rows)
    old.c.write(folder/'task.json',task)
    old.c.write(folder/'start_audit.json',diagnostic)
    for name,value in [('original_start',original),('start_coefficients',b),('start_selection',z),('grid_rows',rows)]:
        np.save(folder/(name+'.npy'),value)
    model,beta,selected=old.build(arrays,settings,task,rows,env)
    try:
        for j in range(292): beta[j].Start=float(b[j]); selected[j].Start=float(z[j])
        model.Params.OutputFlag=0
        old.c.write(folder/'model.json',dict(variables=model.NumVars,constraints=model.NumConstrs,
            binaries=model.NumBinVars,sos=model.NumSOS,
            parameters={k:model.getParamInfo(k)[2] for k in old.PARAMS}))
        model.optimize()
        if model.Status not in (2,9) or model.SolCount < 1: raise ValueError('smoke solve failed')
        b=values(beta); z=values(selected)
        np.save(folder/'coefficients.npy',b); np.save(folder/'selection.npy',z)
        report=old.v.policy.audit(arrays,b,z,task['budget'],rows,settings,ids)
        exact=report['audit']['independent']['regularized_objective_hartree2']
        if not report['passed'] or not np.isclose(model.ObjVal,exact,rtol=1e-7,atol=1e-10):
            raise ValueError('smoke scientific audit failed')
        old.c.write(folder/'result.json',dict(passed=True,status=model.Status,objective=model.ObjVal,
            runtime=model.Runtime,report=report,bound=old.c.d.numeric(model.ObjBound)))
        old.publish(folder)
    finally: model.dispose()
    readback(old,task,root,graph,arrays,ids,settings,rows)


def readback(old,task,root,graph,arrays,ids,settings,rows):
    folder=root/task['id']; old.verify_publication(folder)
    if old.c.read(folder/'task.json')!=task: raise ValueError('smoke task mismatch')
    model=old.c.read(folder/'model.json'); params=model['parameters']
    if (model['variables'],model['constraints'],model['binaries'],model['sos'])!=(584,590+2*len(rows),292,0):
        raise ValueError('smoke dimensions')
    if params['TimeLimit']!=120 or params['Threads']!=16 or params['Seed']!=settings.seed:
        raise ValueError('smoke parameters')
    if not all(params[k]==v for k,v in settings.solver_parameters): raise ValueError('smoke solver settings')
    original,b,z,diagnostic=old.start_inputs(task,root,graph,arrays,ids,settings,rows)
    for name,value in [('original_start',original),('start_coefficients',b),('start_selection',z),('grid_rows',rows)]:
        if not np.array_equal(np.load(folder/(name+'.npy')),value): raise ValueError('smoke start identity')
    old.reader.compare_report(diagnostic,old.c.read(folder/'start_audit.json'))
    report=old.v.policy.audit(arrays,np.load(folder/'coefficients.npy'),np.load(folder/'selection.npy'),
                               task['budget'],rows,settings,ids)
    result=old.c.read(folder/'result.json')
    old.reader.compare_report(report,result['report'])
    if not report['passed'] or not np.isclose(result['objective'],
            report['audit']['independent']['regularized_objective_hartree2'],rtol=1e-7,atol=1e-10):
        raise ValueError('smoke objective/science readback')
