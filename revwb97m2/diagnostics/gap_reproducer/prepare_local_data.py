"""Export research inputs locally; not authorized for external sharing."""
import json
from pathlib import Path
import numpy as np
from revwb97m2.mio import ueg_vector
from revwb97m2.qchem_scalar_features import sha256

root=Path(__file__).resolve().parents[2]
source=root/'results/step15_wls_60s_25658936'
payload={key:np.load(source/filename).tolist() for key,filename in
         [('a','feature_matrix.npy'),('b','target.npy'),('weights','objective_weight.npy')]}
payload['ueg']=ueg_vector('R2').tolist()
payload['source_sha256']={name:sha256(source/name) for name in
                         ('feature_matrix.npy','target.npy','objective_weight.npy')}
out=Path(__file__).parent/'research_inputs.local.json'
text=json.dumps(payload,allow_nan=False)
# Verify float round-trip before publishing a fresh local file.
restored=json.loads(text)
assert all(np.array_equal(payload[k],restored[k]) for k in ('a','b','weights','ueg'))
with out.open('x') as handle:
    handle.write(text+'\n')
print('Exact numerical round-trip verified; local research data:',out)
