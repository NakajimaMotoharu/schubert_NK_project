"""Pure same-source generated closure, credential/closing and normal DB scope contracts."""
import ast,unittest
import pg894_bootstrap_sources as p
class Test(unittest.TestCase):
 def test_complete_generated_surfaces(self):
  f=p.files('a'*64);java=f['Pg894BootstrapExisting.java'];refs=f['pg894_bootstrap_existing.py']
  for v in(p.SOURCE,p.DIGEST,'PG862','PG894-bootstrap-guard','lease.confirmClosed();lease=null;lastPulse=0;'):
   self.assertIn(v,java)
  self.assertEqual(java.count('lease.confirmClosed();lease=null;lastPulse=0;'),2)
  for v in('pg895-bootstrap-before-v1','a'*64,'len(baseline[\'rows\'][\'schubert.batch_runs\'])==584','manager.LoadUnit(unit);manager.RefUnit(unit)','config_same(','pg887-native-stop-v1','75f48ce36cd740e98a801eede7fdbb7f','187002958845'):
   self.assertIn(v,refs)
  self.assertIn('.closing.exec',f['pg894_bootstrap_contract.py']);self.assertIn('for selected in (path,closing)',f['pg894_bootstrap_contract.py'])
  for name,raw in f.items():
   if name.endswith('.py'):ast.parse(raw)
  self.assertNotIn('Pg464CodeOnlyDeployment',java)
 def test_baseline_hash_null_unknown_rejected(self):
  for value in(None,'raw','g'*64):
   with self.assertRaises((AssertionError,TypeError)):p.helper(value)
if __name__=='__main__':unittest.main()
