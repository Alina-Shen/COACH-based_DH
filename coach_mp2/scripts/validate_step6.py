"""Fail-closed Step6 PT2 parser and aggregate validation."""
from pathlib import Path
import json,re,hashlib,math
from validate_step2_fixed import parse as parent_parse
R=Path(__file__).resolve().parents[1];H=Path('/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2/step6_v1')
F=r'[-+]?\d+(?:\.\d*)?(?:[EeDd][-+]?\d+)?'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def number(pattern,text):
 x=re.findall(pattern,text,re.M|re.I)
 if len(x)!=1:raise ValueError('Expected one match: '+pattern)
 v=float(x[0].replace('D','E').replace('d','e'))
 if not math.isfinite(v):raise ValueError('Nonfinite energy')
 return v
def parse_pt2(text,engine):
 if 'Thank you very much for using Q-Chem' not in text:raise ValueError('Missing normal termination')
 label='RIMP2' if engine=='RIMP2' else 'MP2'
 if 'Components of the '+label+' correlation energy:' not in text:raise ValueError('Wrong actual PT2 engine')
 aa=number(r'aaaa\s+correlation energy\s*=\s*('+F+')',text);ab=number(r'abab\s+correlation energy\s*=\s*('+F+')',text);bb=number(r'bbbb\s+correlation energy\s*=\s*('+F+')',text);sing=number(r'non-Brillouin singles\s*=\s*('+F+')',text);total=number(r'Total\s+'+label+r'\s+correlation energy\s*=\s*('+F+')',text)
 ss=aa+bb;os=ab
 if engine=='RIMP2':
  if 'No regularization used' not in text:raise ValueError('Missing no-regularization evidence')
  for key in ['Same     Spin Scaling factor','Opposite Spin Scaling factor']:
   if number(re.escape(key)+r'\s*=\s*('+F+')',text)!=1:raise ValueError('Nonunit spin scale')
  if abs(number(r'total same-spin energy\s*=\s*('+F+')',text)-ss)>2e-8:raise ValueError('SS decomposition failure')
  if abs(number(r'total opposite-spin energy\s*=\s*('+F+')',text)-os)>2e-8:raise ValueError('OS decomposition failure')
 if abs(ss+os+sing-total)>2e-8:raise ValueError('PT2 total closure failure')
 return dict(engine=engine,aa=aa,bb=bb,opposite_spin=os,same_spin=ss,doubles=ss+os,printed_singles=sing,printed_total=total,closure_error=ss+os+sing-total,singles_scale=.3211 if engine=='RIMP2' else 1.,singles_excluded_from_feature=True)
def main():
 protocol=json.loads((R/'manifests/step6_protocol_v1.json').read_text());conv=json.loads((R/'manifests/step6_conventional_v2.json').read_text());denom=json.loads((R/'results/step6_denominator_audit.json').read_text());assert denom['passed'];baseline={c['species']:c['energy']['energy_hartree'] for c in json.loads((R/'results/step5_native_v4_validation.json').read_text())['cases']}
 cases=[c for c in protocol['cases'] if c['engine']=='RIMP2']+conv['cases'];reports=[]
 for c in cases:
  assert sha(Path(c['input']))==c['input_sha256'];text=(H/(c['tag']+'.out')).read_text();v=parse_pt2(text,c['engine']);p=parent_parse(text);assert abs(p['energy_hartree']-baseline[c['species']])<=2e-8;assert abs(p['closure_error_hartree'])<=2e-8
  expected=1 if c['core']=='FC' else 0
  counts=re.findall(r'There are\s+(\d+) alpha and\s+(\d+) beta electrons',text);assert counts==([('5','5')] if c['species']=='SIE4x4_h2o' else [('4','2')])
  if c['engine']=='RIMP2':
   core=re.findall(r'# of frozen core orbitals:\s*(\d+)',text);assert core==(['1'] if expected else [])
  inp=Path(c['input']).read_text()
  for line in ['EXCHANGE COACH','N_FROZEN_CORE '+c['core'],'N_FROZEN_VIRTUAL 0','MAX_SCF_CYCLES 0','MP2_RESTART_NO_SCF TRUE','SCF_GUESS_MIX 0','NO_ORTHO TRUE','GEN_SCFMAN FALSE','SCS 3','SSS_FACTOR 1000000','SOS_FACTOR 1000000']:assert line in inp,line
  if c['engine']=='MP2':assert 'AUX_BASIS' not in inp
  reports.append(dict(tag=c['tag'],species=c['species'],core=c['core'],parent_energy=p['energy_hartree'],pt2=v,output_sha256=sha(H/(c['tag']+'.out'))))
 comparisons=[]
 for name in ['SIE4x4_h2o','16_C_AE18']:
  rows={c['tag']:c['pt2'] for c in reports if c['species']==name};ri=rows[name+'_RIMP2_FC'];mp=rows[name+'_MP2_4center_FC'];ae=rows[name+'_RIMP2_0'];diff=ri['doubles']-mp['doubles'];shift=ae['doubles']-ri['doubles'];comparisons.append(dict(species=name,ri_minus_conventional_hartree=diff,ri_minus_conventional_kcalmol=diff*627.50947406,spin_differences={k:ri[k]-mp[k] for k in ['same_spin','opposite_spin']},all_electron_minus_frozen_core=shift,passed=abs(diff)<=protocol['ri_conventional_tolerance_hartree'] and shift<0))
 build=json.loads((R/'manifests/step5_no_orientation_build_v1.json').read_text());assert sha(Path(build['binary']))==build['binary_sha256']
 report=dict(step=6,passed=all(x['passed'] for x in comparisons),cases=reports,comparisons=comparisons,denominator_audit_sha256=sha(R/'results/step6_denominator_audit.json'),runtime_sha256=build['binary_sha256'],scope='Two-system canonical RI-UMP2 feature gateway; not full-domain production',solver_used=False,singles_convention='SCS3 unit OS/SS; native libgmbpt still scales singles by .3211, legacy conventional by 1.0. Printed singles are diagnostics and excluded from fitted doubles.')
 (R/'results/step6_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));assert report['passed']
if __name__=='__main__':main()
