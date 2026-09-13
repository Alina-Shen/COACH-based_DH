"""Read the user-supplied XLSX without dependencies or modifying the workbook."""
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET
import csv, hashlib, json, posixpath
ROOT=Path(__file__).resolve().parents[1]
BOOK=ROOT.parent/'coach/paper/COACH_raw_data.xlsx'
N={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
REL='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read_book(path):
    with ZipFile(path) as z:
        strings=[]
        if 'xl/sharedStrings.xml' in z.namelist():
            strings=[''.join(t.text or '' for t in si.findall('.//m:t',N)) for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',N)]
        rels={r.attrib['Id']:r.attrib['Target'] for r in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        result={}
        for sheet in ET.fromstring(z.read('xl/workbook.xml')).findall('m:sheets/m:sheet',N):
            target=rels[sheet.attrib['{'+REL+'}id']]
            target=target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/'+target)
            rows=[]
            for row in ET.fromstring(z.read(target)).findall('m:sheetData/m:row',N):
                cells={}
                for cell in row.findall('m:c',N):
                    v=cell.find('m:v',N);value=v.text if v is not None else ''
                    if cell.get('t')=='s':value=strings[int(value)]
                    if cell.get('t')=='inlineStr':value=''.join(t.text or '' for t in cell.findall('.//m:t',N))
                    cells[cell.attrib['r']]=value
                rows.append(cells)
            result[sheet.attrib['name']]=rows
        return result

def main():
    book=read_book(BOOK);raw=book['raw_data']
    assert raw[0]['A1']=='Reaction' and raw[0]['D1']=='COACH' and raw[0]['E1']=='COACH(no 3B)'
    matches=[r for r in raw if any(v=='AE18_6' for v in r.values())];assert len(matches)==1
    row=matches[0];number=next(k[1:] for k,v in row.items() if v=='AE18_6')
    cell='D'+number;energy=float(row[cell])
    authority=Path('/clusterfs/mhg-data/yaoshen/GSCDB/Info/DatasetEval.csv')
    with authority.open() as f:eval_rows=list(csv.DictReader(f))
    mapping=[r for r in eval_rows if r['Reaction']=='AE18_6'];assert len(mapping)==1
    assert mapping[0]['Stoichiometry']=='1,16_C_AE18'
    factor=json.loads((ROOT/'configs/scientific_spec_v1.json').read_text())['units']['hartree_to_kcal_per_mol']
    assert abs(float(row['C'+number])-float(mapping[0]['Reference'])*factor)<1e-8
    pilot=json.loads((ROOT/'results/step2_pilot_v1.json').read_text())
    carbon=next(r for r in pilot['cases'] if r['species']=='16_C_AE18' and r['mode']=='scf')
    ref=energy/factor;delta=carbon['converged_hartree']-ref
    water=[r for r in eval_rows if 'SIE4x4_h2o' in r['Stoichiometry'].split(',')]
    assert all(r['Stoichiometry']!='1,SIE4x4_h2o' for r in water)
    report=dict(source=str(BOOK),source_sha256=sha(BOOK),source_authority='user-supplied COACH paper raw data',
        sheets=list(book),layout='reaction/property values, not a standalone molecular-energy table',
        stoichiometry_authority=str(authority),stoichiometry_sha256=sha(authority),
        conversion_factor=factor,conversion_evidence='frozen scientific spec; GSCDB/Analysis/analyze.ipynb; workbook Reference column consistency',
        carbon=dict(reaction='AE18_6',sheet='raw_data',cell=cell,column='COACH',stoichiometry=mapping[0]['Stoichiometry'],
          reference_kcal_mol=energy,reference_hartree=ref,pilot_hartree=carbon['converged_hartree'],difference_hartree=delta,
          tolerance_hartree=carbon['tolerance_hartree'],passed=carbon['repeatability_pass'] and abs(delta)<carbon['tolerance_hartree']),
        water=dict(direct_absolute_comparison_available=False,related_reactions=water,
          reason='Water enters multicomponent reaction combinations; water-only pilot cannot reconstruct them.',existing_fixture_comparison='PASS'),
        reference_location_resolved=True,step2_complete=False,
        remaining='Dedicated zero-update energy evaluator remains unvalidated; historical generating build remains unknown, as accepted.')
    (ROOT/'results/step2_workbook_reference_v1.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report['carbon'],indent=2));assert report['carbon']['passed']
if __name__=='__main__':main()
