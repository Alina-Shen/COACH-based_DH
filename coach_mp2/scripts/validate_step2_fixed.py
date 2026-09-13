"""Fail-closed native COACH fixed-orbital baseline validation."""
from pathlib import Path
import hashlib,json,re,math,struct,sys
ROOT=Path(__file__).resolve().parents[1]
OUT=Path('/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2/step2_fixed_v3')
FLOAT=r'[-+]?\d+(?:\.\d*)?(?:[EeDd][-+]?\d+)?'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def parse(text):
    if 'Thank you very much for using Q-Chem' not in text:raise ValueError('No normal termination')
    for label in ['The orbitals will not be altered','Avoiding writing the new MOs to disk','Coulomb attenuation parameter = 0.27']:
        if label not in text:raise ValueError('Missing no-update/method evidence: '+label)
    if re.search(r'fatal error|SCF failed|Convergence failure',text,re.I):raise ValueError('Q-Chem failure')
    values={}
    for line in text.splitlines():
        if '=' not in line:continue
        k,v=line.split('=',1);m=re.match(r'\s*('+FLOAT+')',v)
        if m:values[' '.join(k.split())]=float(m[1].replace('D','E').replace('d','e'))
    # This older driver groups semilocal correlation and VV10 in DFT Correlation.
    names=['One-Electron Energy','Total Coulomb Energy','Alpha Exchange Energy','Beta Exchange Energy','DFT Exchange Energy','DFT Correlation Energy','Nuclear Repu. Energy']
    components={k:values[k] for k in names}
    cycles=re.findall(r'^\s*(\d+)\s+('+FLOAT+r')\s+('+FLOAT+r')\s+Convergence criterion met\s*$',text,re.M)
    if len(cycles)!=1 or cycles[0][0]!='1':raise ValueError('Expected single fixed-density Fock evaluation')
    energy=float(cycles[0][1]);total=sum(components.values())
    # With restart/noSCF this message denotes bypass, not optimized convergence.
    return dict(energy_hartree=energy,components=components,component_sum_hartree=total,closure_error_hartree=total-energy,
       dispersion_hartree=values['-D4 energy including 3-body term'],iteration_semantics='one Fock evaluation, no orbital optimization',
       correlation_convention='DFT Correlation includes VV10; do not add it twice')
def density_audit(mo_path, source_density, observed_density, n, occupations):
    def read(p):
        b=Path(p).read_bytes();return struct.unpack('<'+'d'*(len(b)//8),b)
    c=read(mo_path);a=read(source_density);b=read(observed_density)
    if len(c)!=2*n*n+2*n or len(a)!=2*n*n or len(b)!=len(a):raise ValueError('Unexpected MO/density dimensions')
    if not all(math.isfinite(v) for v in (*c,*a,*b)):raise ValueError('Nonfinite orbitals/density')
    worst=0.;delta=0.;passed=True
    for spin,k in enumerate(occupations):
        norm2=math.fsum(c[spin*n*n+orb*n+i]**2 for orb in range(k) for i in range(n))
        bound=16*sys.float_info.epsilon*max(norm2,sys.float_info.min)
        for i in range(n):
            for j in range(n):
                terms=[c[spin*n*n+orb*n+i]*c[spin*n*n+orb*n+j] for orb in range(k)]
                expected=math.fsum(terms);scale=math.fsum(abs(x) for x in terms)
                idx=spin*n*n+i*n+j
                error=max(abs(a[idx]-expected),abs(b[idx]-expected))
                passed=passed and error<=bound
                worst=max(worst,error/bound if bound else 0.)
                delta=max(delta,abs(a[idx]-b[idx]))
    return dict(passed=passed,max_source_to_output_abs=delta,max_fraction_of_roundoff_bound=worst,
                rule='Both densities must equal math.fsum occupied-MO outer products within the normwise roundoff bound 16*epsilon*||C_occ||_F^2 per spin; MO file must be bitwise unchanged',occupations=occupations,nbasis=n)

def main():
    manifest=ROOT/'manifests/step2_fixed_v3.json';m=json.loads(manifest.read_text())
    pilot=json.loads((ROOT/'results/step2_pilot_v1.json').read_text())
    workbook=json.loads((ROOT/'results/step2_workbook_reference_v1.json').read_text())
    checks=[];reports=[]
    for runtime in m['runtime']:checks.append(dict(name='runtime '+runtime['path'],passed=sha(runtime['path'])==runtime['sha256']))
    for case in m['cases']:
        name=case['species'];p=OUT/(name+'_fixed.out');data=parse(p.read_text())
        ref=next(c['reference_hartree'] for c in pilot['cases'] if c['species']==name)
        data.update(species=name,output=str(p),output_sha256=sha(p),reference_hartree=ref,reference_difference_hartree=data['energy_hartree']-ref)
        data['invariance']={}
        for f in case['source_files']:
            checks.append(dict(name=name+' source '+f['path'],passed=sha(f['path'])==f['sha256']))
            n=Path(f['path']).name
            if n in ['53.0','54.0']:
                observed=sha(Path(case['scratch'])/n);match=observed==f['sha256']
                data['invariance'][n]=dict(expected=f['sha256'],observed=observed,passed=match)
                if n=='53.0':checks.append(dict(name=name+' unchanged '+n,passed=match))
        text=p.read_text()
        nbasis=int(re.search(r'There are\s+\d+ shells and\s+(\d+) basis functions',text)[1])
        counts=re.search(r'There are\s+(\d+) alpha and\s+(\d+) beta electrons',text)
        occupations=[int(counts[1]),int(counts[2])]
        source={Path(f['path']).name:f['path'] for f in case['source_files']}
        data['density_reconstruction']=density_audit(source['53.0'],source['54.0'],Path(case['scratch'])/'54.0',nbasis,occupations)
        checks.append(dict(name=name+' independently reconstructed density',passed=data['density_reconstruction']['passed']))
        for key in ['input','source_input']:
            f=case[key];checks.append(dict(name=name+' '+key,passed=sha(f['path'])==f['sha256']))
        controls=Path(case['input']['path']).read_text()
        for control in ['NO_ORTHO TRUE','MP2_RESTART_NO_SCF TRUE','MAX_SCF_CYCLES 0','GEN_SCFMAN FALSE','SCF_GUESS READ','METHOD COACH']:
            checks.append(dict(name=name+' '+control,passed=control in controls))
        checks.append(dict(name=name+' energy reference',passed=abs(data['reference_difference_hartree'])<=2e-6))
        checks.append(dict(name=name+' component closure',passed=abs(data['closure_error_hartree'])<=2e-8))
        if name=='16_C_AE18':
            data['paper_reference_difference_hartree']=data['energy_hartree']-workbook['carbon']['reference_hartree']
            checks.append(dict(name=name+' paper reference',passed=abs(data['paper_reference_difference_hartree'])<=2e-6))
        reports.append(data)
    checks.append(dict(name='paper workbook hash unchanged',passed=sha(workbook['source'])==workbook['source_sha256']))
    result=dict(passed=all(c['passed'] for c in checks),job_id='25821657',manifest_sha256=sha(manifest),checks=checks,cases=reports,
                reference_tolerance_hartree=2e-6,closure_tolerance_hartree=2e-8,scope='two-system Step 2 baseline only; not full-domain feature/MP2 validation')
    (ROOT/'results/step2_fixed_v3_validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    if not result['passed']:raise SystemExit('Step 2 fixed-orbital gate FAIL')
if __name__=='__main__':main()
