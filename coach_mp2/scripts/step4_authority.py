"""Explicit, source-pinned input reconciliation; never rewrite source files."""
from pathlib import Path
import re
from audit_step4_inputs import parse,reference
REFROOT=Path('/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/authoritative_inputs/qchem/gscdb137_v1')
MALFORMED={'BH9_05_17TS':('SCF_GUESS SADMOSCF_CONVERGENCE 7','SCF_GUESS SADMO\nSCF_CONVERGENCE 7'),
 'BH9_05_7TS':('SCF_GUESS SADMOSCF_CONVERGENCE 7','SCF_GUESS SADMO\nSCF_CONVERGENCE 7'),
 'FH51_n-nonane':('SCF_GUESS SADMOMEM_STATIC 8000','SCF_GUESS SADMO\nMEM_STATIC 8000'),
 'ISOL24_i8e':('SCF_GUESS SADMOMEM_STATIC 8000','SCF_GUESS SADMO\nMEM_STATIC 8000')}
HELIUM={'O24x5_he2_'+s for s in ['0.9','1.0','1.2','1.5','2.0','monA','monB']}
AUX={'BigNC_external':'rimp2-def2-TZVPPD','GDB9_W1_F12_external':'rimp2-def2-TZVP'}
def setrem(text,key,value):
 pattern=rf'(?im)^([ \t]*){key}\b\s*(?:=\s*)?[^\r\n]*$'
 # Only within $rem; do not alter comments or named sections.
 m=re.search(r'(?ims)^\s*\$rem\s*\n(.*?)^\s*\$end\s*$',text)
 if not m:raise ValueError('missing rem')
 block=m[1];new,count=re.subn(pattern,key+' '+str(value),block)
 if count>1:raise ValueError('duplicate setting '+key)
 if not count:new=block+key+' '+str(value)+'\n'
 return text[:m.start(1)]+new+text[m.end(1):]
def derive(text,species,prior):
 changes=[];refs=[]
 if species in MALFORMED:
  old,new=MALFORMED[species]
  if text.count(old)!=1:raise ValueError('malformed-line fingerprint changed')
  text=text.replace(old,new);changes.append('split_concatenated_rem_line')
 if species=='AE11_Yb' or species in HELIUM:
  p=REFROOT/prior['snapshot_input'];data=p.read_bytes()
  import hashlib
  if hashlib.sha256(data).hexdigest()!=prior['input_sha256']:raise ValueError('reference input hash changed')
  pinned=data.decode();refs.append(str(p))
  block='aux_basis' if species=='AE11_Yb' else 'basis'
  body=reference.qchem_block(pinned,block,required=True)
  if re.search(r'(?im)^\s*\$'+block+r'\s*$',text):raise ValueError('unexpected preexisting repair block')
  text+='\n$'+block+'\n'+body+'$end\n'
  text=setrem(text,'AUX_BASIS_CORR' if species=='AE11_Yb' else 'BASIS','GEN')
  if species in HELIUM:text=setrem(text,'PURECART','111')
  changes.append('inherit_pinned_'+block+'_definition')
 if prior['scope'] in AUX:
  blocks,rem,*_=parse(text)
  if 'AUX_BASIS_CORR' in rem:raise ValueError('unexpected source auxiliary assignment')
  text=setrem(text,'AUX_BASIS_CORR',AUX[prior['scope']]);changes.append('inherit_explicit_external_auxiliary_assignment')
 blocks,rem,*_=parse(text)
 if rem['METHOD'].upper()!='COACH':text=setrem(text,'METHOD','COACH');changes.append('method_to_COACH')
 # These are input templates, not executable production jobs: later stage derives
 # zero-cycle/no-ortho/grid/PT2 settings with its own validation and resources.
 return text,changes,refs
