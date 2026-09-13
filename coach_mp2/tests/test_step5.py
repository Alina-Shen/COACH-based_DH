import unittest,sys,tempfile,struct
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import inventory_step5 as inv
class TestArchive(unittest.TestCase):
 def test_ghost(self):self.assertEqual(inv.atoms('$molecule\n0 1\n@H 0 0 1\n$end')[2][0][0],'@h')
 def test_nan(self):
  with self.assertRaises(ValueError):inv.atoms('$molecule\n0 1\nH nan 0 0\n$end')
 def test_malformed(self):
  with self.assertRaises(ValueError):inv.atoms('$molecule\n0 1\nH 0 0\n$end')
 def test_dimensions_and_geometry(self):
  root=Path(__file__).resolve().parents[1]/'runtime';root.mkdir(exist_ok=True)
  with tempfile.TemporaryDirectory(dir=root) as tmp:
   p=Path(tmp);folder=p/'test';folder.mkdir();text='$molecule\n0 1\nH 0 0 0\n$end'
   (folder/'molecule').write_text(text);source=p/'input.in';source.write_text(text)
   (folder/'819.0').write_bytes(struct.pack('<4i',3,2,111,0))
   for fn,size in [('53.0',128),('54.0',144),('58.0',144)]:(folder/fn).write_bytes(bytes(size))
   row=dict(species='test',scope='test',source=str(source),orbital_spherical_aos='3')
   old=inv.DEFAULT;inv.DEFAULT=p
   try:
    self.assertEqual(inv.audit(row)['status'],'structural_pass')
    row['orbital_spherical_aos']='4';self.assertIn('basis_dimension',inv.audit(row)['issues'])
    row['orbital_spherical_aos']='3';(folder/'53.0').write_bytes(b'bad');self.assertIn('53.0_size',inv.audit(row)['issues'])
    (folder/'molecule').write_text(text.replace('H 0 0 0','H 1 0 0'));self.assertIn('geometry_coordinates',inv.audit(row)['issues'])
   finally:inv.DEFAULT=old
if __name__=='__main__':unittest.main()

import import_step5 as imp
class TestImport(unittest.TestCase):
 def test_copy_resume_and_corruption(self):
  root=Path(__file__).resolve().parents[1]/'runtime'
  with tempfile.TemporaryDirectory(dir=root) as tmp:
   p=Path(tmp);src=p/'source';src.mkdir();(src/'53.0').write_bytes(b'unchanged source');(src/'Frg1').mkdir()
   old=imp.DEST;imp.DEST=p/'destination'
   try:
    row=dict(species='test',source=str(src));record=imp.one(row)
    self.assertEqual(record['excluded_nested_directories'],['Frg1']);self.assertEqual(imp.one(row),record)
    target=imp.DEST/'species/test/53.0';target.chmod(0o644);target.write_bytes(b'corrupt')
    with self.assertRaises(AssertionError):imp.one(row)
    self.assertEqual((src/'53.0').read_bytes(),b'unchanged source')
   finally:imp.DEST=old
 def test_traversal(self):
  with self.assertRaises(AssertionError):imp.one(dict(species='../escape',source='/nonexistent'))
