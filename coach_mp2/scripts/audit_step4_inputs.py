"""Read current molecular input authority and compare pinned reference chemistry."""
from pathlib import Path
import csv,json,re,math,hashlib,importlib.util
ROOT=Path(__file__).resolve().parents[1]
REF=ROOT.parent/'revwb97m2'
DB=Path('/clusterfs/mhg-data/yaoshen/GSCDB')
# Read-only reuse of the reference block fingerprint convention, never its builder.
spec=importlib.util.spec_from_file_location('reference_parser',REF/'scripts/build_data_role_manifests.py')
reference=importlib.util.module_from_spec(spec);spec.loader.exec_module(reference)
def sha(data):return hashlib.sha256(data).hexdigest()
def csvrows(p):
 with p.open(newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))
def parse(text):
    matches=list(re.finditer(r'(?ims)^\s*\$(\w+)\s*\n(.*?)^\s*\$end\s*$',text))
    blocks={}
    for m in matches:
        key=m[1].lower()
        if key in blocks:raise ValueError('duplicate block '+key)
        blocks[key]=m[2]
    if '@@@' in text:raise ValueError('multi-job input')
    if not {'molecule','rem'}<=set(blocks):raise ValueError('missing required block')
    rem={}
    for raw in blocks['rem'].splitlines():
        line=re.split(r'[!#]',raw)[0].strip()
        if not line:continue
        fields=line.replace('=',' ').split()
        if len(fields)!=2:raise ValueError('malformed rem '+line)
        k,v=fields[0].upper(),fields[1]
        if k in rem and rem[k].upper()!=v.upper():raise ValueError('conflicting rem '+k)
        rem[k]=v
    lines=[re.split(r'[!#]',x)[0].strip() for x in blocks['molecule'].splitlines()]
    lines=[x for x in lines if x]
    header=lines[0].split()
    if len(header)!=2:raise ValueError('charge/spin header')
    charge,mult=map(int,header)
    if mult<1:raise ValueError('invalid multiplicity')
    atoms=[];fragment=False
    for line in lines[1:]:
        if line=='--':fragment=True;continue
        fields=line.split()
        if fragment:
            if len(fields)!=2:raise ValueError('fragment header')
            int(fields[0]);fragment_mult=int(fields[1])
            if fragment_mult<1:raise ValueError('invalid fragment multiplicity')
            fragment=False;continue
        if len(fields)!=4 or not re.fullmatch(r'@?[A-Za-z]{1,3}',fields[0]):raise ValueError('invalid Cartesian atom '+line)
        coords=[float(x.replace('D','E').replace('d','e')) for x in fields[1:]]
        if not all(math.isfinite(x) for x in coords):raise ValueError('nonfinite coordinates')
        atoms.append((fields[0],coords))
    if fragment:raise ValueError('incomplete fragment')
    if not atoms:raise ValueError('empty geometry')
    return blocks,rem,charge,mult,atoms

def main():
    roles=csvrows(ROOT/'manifests/data_roles_v1/species.csv');metadata={r['species']:r for r in csvrows(REF/'manifests/data_roles/qchem_input_metadata.csv')}
    rows=[];problems=[];methods={};overrides=[]
    for i,role in enumerate(roles):
        name=role['species'];prior=metadata[name];scope=prior['scope']
        group={'BigNC_external':'BigNC','GDB9_W1_F12_external':'GDB9-W1-F12'}.get(scope)
        path=(DB/'AdditionalSets'/group/'qchem_inputs' if group else DB/'qchem_inputs')/(name+'.in')
        try:
            data=path.read_bytes();text=data.decode('utf-8-sig');blocks,rem,charge,mult,atoms=parse(text)
            observed=reference.molecule_metadata(text)
            for k in ['molecule_block_sha256','geometry_payload_sha256','charge','multiplicity','atom_count','real_atom_count','ghost_atom_count','elements']:
                if str(observed[k])!=prior[k]:raise ValueError('reference mismatch '+k)
            for block,prefix in [('basis','basis'),('aux_basis','auxiliary_basis'),('ecp','ecp')]:
                h,n=reference.optional_block_metadata(text,block)
                if h!=prior[prefix+'_block_sha256'] or n!=int(prior[prefix+'_block_bytes']):raise ValueError('reference mismatch '+block)
            for actual,key in [('BASIS','qchem_rem_basis'),('AUX_BASIS_CORR','qchem_rem_auxiliary_basis'),('ECP','qchem_rem_ecp')]:
                if rem.get(actual,'').upper()!=prior[key].upper():raise ValueError('reference mismatch '+actual)
            if rem.get('UNRESTRICTED','').upper()!='TRUE':raise ValueError('not UKS')
            if 'METHOD' not in rem:raise ValueError('no METHOD selector')
            for key in ['BASIS','AUX_BASIS_CORR']:
                if rem.get(key,'').upper() in ['GEN','GENERAL'] and ('basis' if key=='BASIS' else 'aux_basis') not in blocks:raise ValueError('missing embedded '+key)
            selected={k:v for k,v in rem.items() if k in ['OMEGA','OMEGA2','HF_SR','HF_LR','DFT_D','DFT_D4_S6','DFT_D4_S8','DFT_D4_S9','NL_VV_B','NL_VV_C','EXCHANGE','CORRELATION']}
            if selected:overrides.append(dict(species=name,settings=selected))
            methods[rem['METHOD']]=methods.get(rem['METHOD'],0)+1
            row=dict(species=name,source=str(path),source_sha256=sha(data),scope=scope,**observed,
                orbital_basis=rem.get('BASIS',''),auxiliary_basis=rem.get('AUX_BASIS_CORR',''),ecp=rem.get('ECP',''),
                source_method=rem['METHOD'],target_method='COACH',source_rem=rem,
                block_hashes={k:sha(v.encode()) for k,v in blocks.items()},
                role_flags={k:v for k,v in role.items() if k!='species'},input_bytes=len(data),
                coordinate_units=rem.get('INPUT_BOHR','FALSE').upper(),orbital_files_read=False)
            rows.append(row)
        except Exception as e:problems.append(dict(species=name,path=str(path),error=str(e)))
        if (i+1)%3000==0:print('Audited',i+1,flush=True)
    report=dict(passed=not problems and len(rows)==17452,expected=17452,validated=len(rows),problems=problems,explicit_method_overrides=overrides,source_methods=methods,scope='energy-role molecular input chemistry only; no archive compatibility or PT2 validation',rows=rows,
        source_metadata_sha256=sha((REF/'manifests/data_roles/qchem_input_metadata.csv').read_bytes()),reference_parser_sha256=sha((REF/'scripts/build_data_role_manifests.py').read_bytes()))
    archived=Path('/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2/step4_inputs_v1/initial_audit.json')
    if not archived.exists():raise FileNotFoundError('Full initial audit must be stored under the permitted heavy-data root; rerun only after staging or supply a new versioned workflow')
    summary={k:v for k,v in report.items() if k!='rows'}
    summary['historical_full_audit']=str(archived)
    (ROOT/'results/step4_source_audit_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='rows'},indent=2))
if __name__=='__main__':main()
