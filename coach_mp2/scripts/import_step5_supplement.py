"""Preserve the four initially quarantined sources; release gates remain separate."""
from active_input_authority import load_rows
from import_step5 import one,ROOT
import json

def main():
 rows={r['species']:r for r in load_rows()};records=[]
 for name in ['He3_47','He3_48','He3_49','ISOL24_i8e']:
  r=rows[name];r['source']='/global/scratch/users/jsliang/COACH3/'+name;records.append(one(r));print('Preserved',name,flush=True)
 (ROOT/'results/step5_supplement_import.json').write_text(json.dumps(dict(imported=4,species=[r['species'] for r in records],basis_amendment='configs/input_basis_amendments_v1.json',scope='Verified immutable source preservation; native gate remains separate'),indent=2)+'\n')
if __name__=='__main__':main()
