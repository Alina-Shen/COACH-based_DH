"""Stage immutable source+COACH input tar and independently resolve basis metadata."""
from pathlib import Path
import os,sys,csv,json,hashlib,tarfile,io,collections
ROOT=Path(__file__).resolve().parents[1]
os.environ['TMPDIR']=str(ROOT/'runtime')
sys.path.insert(0,str(ROOT.parent/'revwb97m2/scripts'))
from audit_step4_inputs import parse,csvrows,reference,DB
from step4_authority import derive,AUX
from pyscf_basis_bridge import resolve_record,canonical_hash,QCHEM_AUXILIARY_FILES
from build_basis_bridge import molecular_dimensions
HEAVY=Path('/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2/step4_inputs_v1')
REF=ROOT.parent/'revwb97m2'
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
 if HEAVY.exists():raise FileExistsError('Snapshot already exists')
 meta={r['species']:r for r in csvrows(REF/'manifests/data_roles/qchem_input_metadata.csv')}
 expected={r['species']:r for r in csvrows(REF/'manifests/basis_bridge/resolved_basis_records.csv')}
 roles=csvrows(ROOT/'manifests/data_roles_v1/species.csv')
 HEAVY.mkdir(parents=True);cache={};summaries=[];counts=collections.Counter();references={};failures=[]
 with tarfile.open(HEAVY/'inputs.tar','x') as tar,(HEAVY/'metadata.jsonl').open('x') as records:
  for i,role in enumerate(roles):
   name=role['species'];prior=meta[name];group={'BigNC_external':'BigNC','GDB9_W1_F12_external':'GDB9-W1-F12'}.get(prior['scope'])
   source=(DB/'AdditionalSets'/group/'qchem_inputs' if group else DB/'qchem_inputs')/(name+'.in')
   raw=source.read_bytes();text,changes,refpaths=derive(raw.decode('utf-8-sig'),name,prior)
   blocks,rem,charge,mult,atoms=parse(text)
   for p in refpaths:references[p]=sha(Path(p).read_bytes())
   observed=reference.molecule_metadata(text)
   for k in ['molecule_block_sha256','geometry_payload_sha256','charge','multiplicity','atom_count','real_atom_count','ghost_atom_count','elements']:
    if str(observed[k])!=prior[k]:raise ValueError(name+' geometry '+k)
   for block,prefix in [('basis','basis'),('aux_basis','auxiliary_basis'),('ecp','ecp')]:
    h,n=reference.optional_block_metadata(text,block)
    if h!=prior[prefix+'_block_sha256']:raise ValueError(name+' definition '+block)
   if rem['BASIS'].upper()!=prior['qchem_rem_basis'].upper():raise ValueError(name+' orbital basis')
   if rem['AUX_BASIS_CORR'].upper()!=(AUX.get(prior['scope'],prior['qchem_rem_auxiliary_basis'])).upper():raise ValueError(name+' auxiliary basis')
   if rem.get('ECP','').upper()!=prior['qchem_rem_ecp'].upper():raise ValueError(name+' ECP')
   if rem['UNRESTRICTED'].upper()!='TRUE' or rem['METHOD'].upper()!='COACH':raise ValueError(name+' method/spin')
   elements=sorted({label.lstrip('@').capitalize() for label,_ in atoms})
   geometry='\n'.join(('ghost-'+label[1:] if label.startswith('@') else label)+' '+' '.join(map(str,xyz)) for label,xyz in atoms)
   record={'identity':{'scope':prior['scope']},'pyscf_molecule':{'elements':elements}}
   for key,block,selector in [('orbital_basis','basis','BASIS'),('auxiliary_basis','aux_basis','AUX_BASIS_CORR'),('ecp','ecp','ECP')]:
    label=rem.get(selector,'')
    # Invoke the pinned reference's explicit scope policy for missing-source aux;
    # independently require its result equals the assigned template label.
    if key=='auxiliary_basis' and prior['scope'] in AUX:label=''
    record[key]={'qchem_rem_label':label,'embedded_block':{'present':bool(blocks.get(block)), 'qchem_block':blocks.get(block,'')}}
   key=canonical_hash(record)
   if key not in cache:cache[key]=resolve_record(record)
   resolved=cache[key]
   dimensions=molecular_dimensions(geometry,charge,resolved['orbital_basis'],resolved['ecp']);adim=molecular_dimensions(geometry,charge,resolved['auxiliary_basis'],{})
   checks={'orbital_definition_sha256':canonical_hash(resolved['orbital_basis']),'auxiliary_definition_sha256':canonical_hash(resolved['auxiliary_basis']),'ecp_definition_sha256':canonical_hash(resolved['ecp']),
       'electron_count':dimensions['electrons'],'ecp_electrons':dimensions['ecp_electrons'],'orbital_shells':dimensions['nbas'],'orbital_spherical_aos':dimensions['nao'],'auxiliary_shells':adim['nbas'],'auxiliary_spherical_aos':adim['nao']}
   for k,v in checks.items():
    if str(v)!=expected[name][k]:raise ValueError(name+' resolved mismatch '+k)
   if dimensions['electrons']<mult-1 or (dimensions['electrons']-(mult-1))%2:raise ValueError(name+' spin parity')
   data=text.encode();info=dict(species=name,scope=prior['scope'],source=str(source),source_sha256=sha(raw),derived_sha256=sha(data),changes=changes,reference_inputs=refpaths,
       orbital_basis=rem['BASIS'],auxiliary_basis=rem['AUX_BASIS_CORR'],ecp_label=rem.get('ECP',''),source_method=reference.rem_values(raw.decode('utf-8-sig')).get('METHOD',''),target_method='COACH',
       block_hashes={k:sha(v.encode()) for k,v in blocks.items()},role_flags=role,**observed,**checks,ecp_resolution=resolved['ecp_resolution'])
   records.write(json.dumps(info,sort_keys=True)+'\n')
   for prefix,payload in [('source',raw),('coach',data)]:
    member=tarfile.TarInfo(prefix+'/'+name+'.in');member.size=len(payload);member.mode=0o444;member.mtime=0;tar.addfile(member,io.BytesIO(payload))
   summaries.append({k:info[k] for k in ['species','scope','source','source_sha256','derived_sha256','orbital_basis','auxiliary_basis','ecp_label','charge','multiplicity','atom_count','ghost_atom_count','electron_count','ecp_electrons','orbital_shells','orbital_spherical_aos','auxiliary_shells','auxiliary_spherical_aos','ecp_resolution']})
   counts.update(changes)
   if (i+1)%3000==0:print('Staged and resolved',i+1,flush=True)
 with (ROOT/'manifests/step4_inputs_v1.csv').open('x',newline='') as f:w=csv.DictWriter(f,fieldnames=list(summaries[0]));w.writeheader();w.writerows(summaries)
 # Retain the initial 12-difference audit in the heavy-data root.
 audit=ROOT/'results/step4_input_audit.json'
 if audit.exists():
  (HEAVY/'initial_audit.json').write_bytes(audit.read_bytes());audit.unlink()
 pins=[REF/'configs/scientific_spec.yaml',REF/'manifests/data_roles/qchem_input_metadata.csv',REF/'manifests/basis_bridge/resolved_basis_records.csv',REF/'manifests/basis_bridge/step6_basis_bridge_v1.yaml',REF/'scripts/pyscf_basis_bridge.py',REF/'scripts/build_basis_bridge.py',REF/'scripts/build_data_role_manifests.py',*QCHEM_AUXILIARY_FILES.values()]
 references.update({str(p):sha(p.read_bytes()) for p in pins})
 result=dict(status='prepared_not_yet_independently_validated',species=len(summaries),changes=dict(counts),snapshot=str(HEAVY),artifacts={p.name:sha(p.read_bytes()) for p in HEAVY.iterdir()},source_pins=references,
   manifest_sha256=sha((ROOT/'manifests/step4_inputs_v1.csv').read_bytes()),no_solver_used=True,no_orbitals_read=True,no_quantum_jobs=True,definition_cache_entries=len(cache),
   auxiliary_library_policy='hash-pinned reference Q-Chem assets; no runtime automatic generation',production_templates=False)
 (ROOT/'manifests/step4_snapshot_v1.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k not in ['source_pins','artifacts']},indent=2))
if __name__=='__main__':main()
