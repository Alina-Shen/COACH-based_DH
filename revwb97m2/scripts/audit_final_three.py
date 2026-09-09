from pathlib import Path
import numpy as np
from revwb97m2.scripts import refresh_water_scalar_v1 as w, embedded_y_features_v1 as y
v=w.v
records=[]
vector,fixed=w.validate()
root=Path(v.read(w.BASE)['output_root'])/w.NAME
water=v.read(root/'water_refresh.json')
records.append(dict(species=w.NAME,job='25726543',passed=True,stages=1,
    hf_error_hartree=fixed['pure_hf_reconstruction_error_hartree'],
    publication_sha256=v.digest(root/'water_refresh.json'),**{k:water[k] for k in ('old_vv10_hartree','new_vv10_hartree','sr_reuse_error_hartree')}))
for i,name in enumerate(y.NAMES):
    vector,fixed,grids=y.validate(name)
    root=Path(v.read(y.PLAN)['output_root'])/name
    records.append(dict(species=name,job=f'25726544_{i}',passed=True,stages=6,
        hf_error_hartree=fixed['pure_hf_reconstruction_error_hartree'],
        publication_sha256=v.digest(root/'species.json'),finite=bool(np.isfinite(vector).all())))
target=v.ROOT/'results/pilot_execution_v3/final_three_readback_20260908.json'
assert not target.exists()
v.write(target,dict(passed=True,cases=records,total_stages=13))
print(records,flush=True)
