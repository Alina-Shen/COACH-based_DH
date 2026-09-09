"""Assemble the exact pilot from audited generic, corrected legacy and native gap evidence."""
import hashlib
from pathlib import Path
import numpy as np
from revwb97m2.scripts import generate_training_features_v2 as g


def collect():
    out=g.ROOT/'results/pilot_execution_v3'
    reports=[out/'first16_independent_readback_20260908.json',out/'remaining166_independent_readback_20260908.json']
    audited={}
    for path in reports:
        data=g.native.read(path)
        g.native.require(data['passed'],'failed prerequisite audit')
        for case in data['cases']:
            g.native.require(case['passed'] and case['species'] not in audited,'invalid or duplicate audit case')
            audited[case['species']]={**case,'plan_sha256':case.get('plan_sha256',data.get('plan_sha256'))}
    records={}
    base=g.ROOT/'manifests/production_generator'
    paths=[base/'training_first16_v3.json',*[base/f'pilot_remaining_v3/pilot_remaining_v3_m{m}.json' for m in (14,21,35,227)]]
    for path in paths:
        plan,_=g.load(path)
        for case in plan['cases']:
            name=case['species'];root=Path(plan['output_root'])/name
            g.native.require(g.native.digest(path)==audited[name]['plan_sha256'],'plan changed since audit')
            g.native.require(g.native.digest(root/'species.json')==audited[name]['publication_sha256'],'publication changed since audit')
            pub=g.native.read(root/'species.json')
            g.native.require(all(g.native.digest(root/p)==h for p,h in pub['artifacts'].items()),'artifact changed since audit')
            records[name]=(np.load(root/'ready/feature_vector_292.npy'),g.native.read(root/'ready/fixed_energy.json'),
                {grid:np.load(root/f'ready/grid_difference_{grid}.npy') for grid in ('99590','75302')})
    legacy_path=out/'legacy38_corrected_audit_20260908.json'
    legacy=g.native.read(legacy_path)
    g.native.require(legacy['passed'] and legacy['accepted']==38,'legacy audit incomplete')
    for case in legacy['cases']:
        vector=Path(case['vector_path']);root=vector.parent.parent
        g.native.require(g.native.digest(vector)==case['vector_sha256'] and
            g.native.digest(root/'species.json')==case['publication_sha256'] and
            g.native.digest(case['fixed_output'])==case['fixed_output_sha256'],'legacy evidence changed since audit')
        pub=g.native.read(root/'species.json')
        g.native.require(all(g.native.digest(root/p)==h for p,h in pub['artifacts'].items()),'legacy artifact changed')
        records[case['species']]=(np.load(vector),case['corrected_fixed'],
            {key:np.load(path) for key,path in case['grid_paths'].items()})
    records.update(g.corrected.validate_registry())
    from revwb97m2.scripts import refresh_water_scalar_v1 as w, embedded_y_features_v1 as y
    vector,fixed=w.validate()
    water_root=Path(g.native.read(w.BASE)['output_root'])/w.NAME
    records[w.NAME]=(vector,fixed,{grid:np.load(water_root/f'ready/grid_difference_{grid}.npy') for grid in ('99590','75302')})
    for name in y.NAMES:
        records[name]=y.validate(name)
    authorities={str(p):g.native.digest(p) for p in [*reports,legacy_path,w.BASE,w.CONTRACT,y.PLAN,g.corrected.REGISTRY]}
    for path in paths:
        authorities[str(path)]=g.native.digest(path)
    authorities[str(water_root/'water_refresh.json')]=g.native.digest(water_root/'water_refresh.json')
    yp=g.native.read(y.PLAN)
    for name in y.NAMES:
        path=Path(yp['output_root'])/name/'species.json'
        authorities[str(path)]=g.native.digest(path)
    return records,authorities


def assemble_checked(reactions,records):
    g.native.require(len(reactions)==100,'exact100 reactions required')
    names={t['species'] for r in reactions for t in r['stoichiometry']}
    g.native.require(len(names)==224 and names<=set(records),'exact224 species required')
    arrays=g.corrected.assemble_with_evidence(reactions,records)
    g.native.require(arrays['feature_matrix'].shape==(100,292),'wrong matrix shape')
    # Independently form a stoichiometry matrix and check every assembled channel.
    names=sorted(names);index={name:i for i,name in enumerate(names)}
    S=np.zeros((100,224))
    for i,reaction in enumerate(reactions):
        for term in reaction['stoichiometry']:
            S[i,index[term['species']]]+=float(term['coefficient'])
    expected=S@np.stack([records[n][0] for n in names])
    np.testing.assert_allclose(arrays['feature_matrix'],expected,rtol=1e-12,atol=2e-10)
    fixed=S@np.array([records[n][1]['fixed_energy_hartree'] for n in names])
    np.testing.assert_allclose(arrays['fixed_energy'],fixed,rtol=1e-12,atol=2e-10)
    for grid in ('99590','75302'):
        expected_grid=S@np.stack([records[n][2][grid] for n in names])
        np.testing.assert_allclose(arrays['grid_differences'][grid],expected_grid,rtol=1e-12,atol=2e-10)
    np.testing.assert_array_equal(arrays['objective_weight'],[r['objective_weight'] for r in reactions])
    np.testing.assert_array_equal(arrays['reference_energy'],[r['reference_hartree'] for r in reactions])
    np.testing.assert_array_equal(arrays['target'],arrays['reference_energy']-arrays['fixed_energy'])
    return arrays,names


def main():
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    g.native.require(not a.output.exists(),'preserve prior export')
    records,authorities=collect()
    source=g.ROOT/'results/training_preflight_v2/pilot100_reactions.json'
    reactions=g.native.read(source);arrays,names=assemble_checked(reactions,records)
    flat={k:v for k,v in arrays.items() if isinstance(v,np.ndarray)}
    flat.update({f'grid_difference_{k}':v for k,v in arrays['grid_differences'].items()})
    g.native.require(all(np.isfinite(v).all() for v in flat.values()),'nonfinite export')
    a.output.mkdir(parents=True)
    for key,value in flat.items():
        path=a.output/(key+'.npy');np.save(path,value)
        np.testing.assert_array_equal(np.load(path,allow_pickle=False),value)
    g.native.write(a.output/'reactions.json',reactions)
    g.native.write(a.output/'species.json',names)
    report=dict(passed=True,entries=100,species=224,features=292,
        reaction_names=arrays['reaction_names'],source_reactions_sha256=g.native.digest(source),
        specification_sha256=g.native.load_fit_settings().specification_sha256,
        code_sha256=g.native.digest(__file__),authorities=authorities,
        artifacts={str(p.relative_to(a.output)):g.native.digest(p) for p in a.output.iterdir()},
        note='Exact100 original reactions/weights; independently checked stoichiometry multiplication; corrected legacy fixed energies explicitly ingested. Numerical matrix acceptance, not MIO or optimality certification.')
    g.native.write(a.output/'validation.json',report)
    (a.output/'MATRIX_COMPLETE').write_text(g.native.digest(a.output/'validation.json')+'\n')
    print('PASS100 entries224 species292 features; export/readback complete',flush=True)


if __name__=='__main__':main()
