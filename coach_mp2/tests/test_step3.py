import csv,importlib.util,json,math,shutil,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from step3_metrics import dataset_metric,evaluate_development
from validate_step3_roles import audit,DATA
class MetricsTests(unittest.TestCase):
 def rule(self,kind='MAE',**kw):return dict(kind=kind,standard_metric=2.,offset=0.,weights={},**kw)
 def test_mae_not_rmse(self):self.assertEqual(dataset_metric(self.rule(),[('a',1,0),('b',3,0)]),(2.,1.))
 def test_relative(self):self.assertEqual(dataset_metric(self.rule('MARE'),[('a',2,1),('b',6,4)]),(0.75,0.375))
 def test_dipole_floor(self):self.assertEqual(dataset_metric(self.rule('regularized_MAE'),[('a',0.5,0),('b',3,2)]),(0.5,0.25))
 def test_weighted_sum_plus_offset(self):
  r=self.rule('weighted_absolute_sum');r.update(weights={'a':2.,'b':3.},offset=0.5)
  self.assertEqual(dataset_metric(r,[('a',1,0),('b',2,0)]),(8.5,4.25))
 def test_zero_relative_reference(self):
  with self.assertRaises(ValueError):dataset_metric(self.rule('MARE'),[('a',1,0)])
 def test_nonfinite(self):
  with self.assertRaises(ValueError):dataset_metric(self.rule(),[('a',float('nan'),0)])
 def test_duplicate(self):
  with self.assertRaises(ValueError):dataset_metric(self.rule(),[('a',1,0),('a',2,0)])
 def test_zero_standard(self):
  r=self.rule();r['standard_metric']=0
  with self.assertRaises(ValueError):dataset_metric(r,[('a',1,0)])
 def test_weighted_missing_row(self):
  r=self.rule('weighted_absolute_sum');r['weights']={'a':1,'b':1}
  with self.assertRaises(ValueError):dataset_metric(r,[('a',1,0)])
 def test_final_or_extra_predictions_rejected(self):
  with self.assertRaises(ValueError):evaluate_development({},[{'reaction':'a','model_selection':True}],{'a':(1,0),'final':(2,0)})
 def test_missing_predictions_rejected(self):
  with self.assertRaises(ValueError):evaluate_development({},[{'reaction':'a','model_selection':True}],{})
 def test_overall_not_mean_of_categories(self):
  policy={'metrics':{'datasets':[dict(dataset=d,category=c,**self.rule()) for d,c in [('AE11','A'),('MB08-165','A'),('MB16-43','B')]]}}
  rows=[dict(reaction=d,dataset=d,model_selection=True) for d in ['AE11','MB08-165','MB16-43']]
  result=evaluate_development(policy,rows,{'AE11':(0,0),'MB08-165':(0,0),'MB16-43':(6,0)})
  self.assertEqual(result['overall_mean_ner'],1.);self.assertEqual(result['category_mean_ner'],{'A':0.,'B':3.})
class RoleTests(unittest.TestCase):
 def mutate(self,filename,action):
  with tempfile.TemporaryDirectory(dir=ROOT/'runtime') as tmp:
   target=Path(tmp)/'roles';shutil.copytree(DATA,target)
   p=target/filename
   with p.open(newline='') as f:rows=list(csv.DictReader(f));fields=list(rows[0])
   action(rows)
   with p.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
   with self.assertRaises(ValueError):audit(target,check_sources=False)
 def test_dropped_row(self):self.mutate('reactions.csv',lambda r:r.pop())
 def test_reordered_rows(self):self.mutate('reactions.csv',lambda r:r.reverse())
 def test_final_leakage(self):self.mutate('reactions.csv',lambda r:r[-1].update(coefficient_fitting='True'))
 def test_bad_stoichiometry(self):self.mutate('reactions.csv',lambda r:r[0].update(stoichiometry='1,WRONG'))
 def test_weight_not_squared(self):self.mutate('source/coach_si_table2_final_cycle_entries.csv',lambda r:r[0].update(objective_weight='100'))
 def test_species_role_tampering(self):self.mutate('species.csv',lambda r:r[0].update(model_selection='False' if r[0]['model_selection']=='True' else 'True'))
if __name__=='__main__':unittest.main()
