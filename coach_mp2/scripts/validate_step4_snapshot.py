"""Read back every archived input, independently enforce allowed transformations."""
from pathlib import Path
import csv,json,tarfile,hashlib,collections
from audit_step4_inputs import parse,csvrows,reference
from step4_authority import MALFORMED,HELIUM,AUX
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def check_transformation(original,derived,name,scope):
 if name in MALFORMED:
  old,new=MALFORMED[name]
  if original.count(old)!=1:raise ValueError('repair source changed')
  original=original.replace(old,new)
 ob,ore,*_=parse(original);db,dre,*_=parse(derived)
 allowed_blocks={'rem'}|({'aux_basis'} if name=='AE11_Yb' else {'basis'} if name in HELIUM else set())
 if not set(ob)<=set(db):raise ValueError('removed source block')
 if any(ob[k]!=db.get(k) for k in ob if k not in allowed_blocks):raise ValueError('unauthorized block change')
 if set(db)-set(ob)-allowed_blocks:raise ValueError('unauthorized new block')
 allowed={'METHOD'}|({'AUX_BASIS_CORR'} if name=='AE11_Yb' or scope in AUX else set())|({'BASIS','PURECART'} if name in HELIUM else set())
 changed={k for k in set(ore)|set(dre) if ore.get(k)!=dre.get(k)}
 if not changed<=allowed:raise ValueError('unauthorized rem change '+str(changed-allowed))
 if dre['METHOD'].upper()!='COACH' or dre['UNRESTRICTED'].upper()!='TRUE':raise ValueError('wrong method/spin')
 if scope in AUX and dre.get('AUX_BASIS_CORR')!=AUX[scope]:raise ValueError('wrong external auxiliary')
 if name=='AE11_Yb' and dre.get('AUX_BASIS_CORR')!='GEN':raise ValueError('wrong Yb auxiliary')
 if name in HELIUM and (dre.get('BASIS')!='GEN' or dre.get('PURECART')!='111'):raise ValueError('wrong helium basis controls')
 return db,dre

def main():
 pointer=json.loads((ROOT/'manifests/step4_snapshot_v1.json').read_text());heavy=Path(pointer['snapshot'])
 assert all(sha(p)==h for p,h in pointer['source_pins'].items()),'source/library drift'
 assert all(sha(heavy/p)==h for p,h in pointer['artifacts'].items()),'snapshot corruption'
 assert sha(ROOT/'manifests/step4_inputs_v1.csv')==pointer['manifest_sha256']
 index=csvrows(ROOT/'manifests/step4_inputs_v1.csv');roles=csvrows(ROOT/'manifests/data_roles_v1/species.csv')
 assert [r['species'] for r in index]==[r['species'] for r in roles] and len(index)==17452
 meta={r['species']:r for r in csvrows(ROOT.parent/'revwb97m2/manifests/data_roles/qchem_input_metadata.csv')}
 bridge={r['species']:r for r in csvrows(ROOT.parent/'revwb97m2/manifests/basis_bridge/resolved_basis_records.csv')}
 with (heavy/'metadata.jsonl').open() as f:detail=[json.loads(line) for line in f]
 assert len(detail)==len(index)
 counters=collections.Counter();ecps=collections.Counter();basis=collections.Counter();aux=collections.Counter()
 with tarfile.open(heavy/'inputs.tar','r') as tar:
  members=tar.getmembers();assert len(members)==34904 and len({m.name for m in members})==34904
  for i,(r,d) in enumerate(zip(index,detail)):
   name=r['species'];assert name==d['species']
   source=tar.extractfile('source/'+name+'.in').read();target=tar.extractfile('coach/'+name+'.in').read()
   assert hashlib.sha256(source).hexdigest()==sha(r['source'])==r['source_sha256']
   assert hashlib.sha256(target).hexdigest()==r['derived_sha256']
   blocks,rem=check_transformation(source.decode('utf-8-sig'),target.decode(),name,r['scope'])
   observed=reference.molecule_metadata(target.decode())
   for k in ['geometry_payload_sha256','molecule_block_sha256','charge','multiplicity','atom_count','ghost_atom_count']:
    assert str(observed[k])==meta[name][k]
   for b,prefix in [('basis','basis'),('aux_basis','auxiliary_basis'),('ecp','ecp')]:
    h,_=reference.optional_block_metadata(target.decode(),b);assert h==meta[name][prefix+'_block_sha256']
   assert rem['BASIS'].upper()==meta[name]['qchem_rem_basis'].upper()
   assert rem['AUX_BASIS_CORR'].upper()==AUX.get(r['scope'],meta[name]['qchem_rem_auxiliary_basis']).upper()
   for k in ['orbital_definition_sha256','auxiliary_definition_sha256','ecp_definition_sha256','electron_count','ecp_electrons','orbital_shells','orbital_spherical_aos','auxiliary_shells','auxiliary_spherical_aos']:
    assert str(d[k])==bridge[name][k]
   assert int(r['electron_count'])>=int(r['multiplicity'])-1 and (int(r['electron_count'])-(int(r['multiplicity'])-1))%2==0
   assert d['role_flags']==roles[i]
   counters.update(d['changes']);ecps[r['ecp_resolution']]+=1;basis[bool(blocks.get('basis'))]+=1;aux[bool(blocks.get('aux_basis'))]+=1
   if (i+1)%4000==0:print('Verified',i+1,flush=True)
 # Confirm auxiliary library content agrees with the already frozen reference policy.
 import yaml
 policy=yaml.safe_load((ROOT.parent/'revwb97m2/manifests/basis_bridge/step6_basis_bridge_v1.yaml').read_text())
 library=policy['translation']['qchem_auxiliary_library'];library_checks={}
 for name,data in library['files'].items():
  p=Path(library['root'])/data['path'];library_checks[name]=sha(p)==data['sha256'];assert library_checks[name]
 runtime_root=Path('/global/home/groups-sw/mhg/qchem_public/qchem_620/qcaux/basis')
 runtime_checks={}
 for name,data in library['files'].items():
  p=runtime_root/Path(data['path']).name;runtime_checks[str(p)]=sha(p)==data['sha256'];assert runtime_checks[str(p)]
 report=dict(passed=True,validated_inputs=17452,archive_members=34904,checks_per_input=['source hashes','derived hashes','allowed transformations only','geometry charge spin','basis auxiliary ECP','reference definition hashes and dimensions','electron spin parity','role order and membership'],
   changes=dict(counters),ecp_resolutions=dict(ecps),embedded_orbital_count=basis[True],embedded_auxiliary_count=aux[True],auxiliary_library_checks=library_checks,current_runtime_auxiliary_library_checks=runtime_checks,
   solver_used=False,orbital_compatibility_validated=False,OPT_included=False)
 (ROOT/'results/step4_validation.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
