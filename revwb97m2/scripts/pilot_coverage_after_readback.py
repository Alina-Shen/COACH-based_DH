"""Diagnose exact pilot gaps and assemble covered rows without changing training scope."""
import hashlib
from pathlib import Path
import numpy as np
from revwb97m2.scripts import generate_training_features_v2 as g


def main():
    out=g.ROOT/'results/pilot_execution_v3'
    reports=[out/'first16_independent_readback_20260908.json',out/'remaining166_independent_readback_20260908.json']
    audited={}
    for path in reports:
        data=g.native.read(path)
        g.native.require(data['passed'],'failed prerequisite audit')
        for case in data['cases']:
            g.native.require(case['passed'] and case['species'] not in audited,'invalid or duplicate audit case')
            audited[case['species']]=case
    records={}
    base=g.ROOT/'manifests/production_generator'
    paths=[base/'training_first16_v3.json',*[base/f'pilot_remaining_v3/pilot_remaining_v3_m{m}.json' for m in (14,21,35,227)]]
    for path in paths:
        plan=g.native.read(path)
        for case in plan['cases']:
            name=case['species'];root=Path(plan['output_root'])/name
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
    reactions=g.native.read(g.ROOT/'results/training_preflight_v2/pilot100_reactions.json')
    species={t['species'] for r in reactions for t in r['stoichiometry']}
    gaps=[dict(reaction=r['reaction'],missing_species=sorted({t['species'] for t in r['stoichiometry']}-set(records)))
          for r in reactions if {t['species'] for t in r['stoichiometry']}-set(records)]
    ready=[r for r in reactions if not ({t['species'] for t in r['stoichiometry']}-set(records))]
    arrays=g.corrected.assemble_with_evidence(ready,records)
    result=dict(pilot_entries=len(reactions),pilot_species=len(species),covered_species=len(species&set(records)),
        missing_species=sorted(species-set(records)),diagnostic_assembled_entries=len(ready),blocked_entries=gaps,
        array_shapes={key:list(value.shape) for key,value in arrays.items() if isinstance(value,np.ndarray)},
        feature_matrix_sha256=hashlib.sha256(arrays['feature_matrix'].tobytes()).hexdigest(),
        finite=all(np.isfinite(value).all() for value in arrays.values() if isinstance(value,np.ndarray) and value.dtype.kind in 'fc'),
        authorities={str(p):g.native.digest(p) for p in [*reports,legacy_path]},
        note='Diagnostic assembly only, NOT a replacement training pilot or fitting release. Original100 entries/weights retained; no missing-feature zero fill. Legacy corrected fixed values explicitly consumed from audit.')
    g.native.write(out/'pilot_coverage_after_readback_20260908.json',result)
    print(result,flush=True)


if __name__=='__main__':
    main()
