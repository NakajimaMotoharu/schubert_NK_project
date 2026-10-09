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
 def test_all_transitive_local_imports_are_present(self):
  files=p.files('a'*64)
  for name,raw in files.items():
   if not name.endswith('.py'):continue
   for node in ast.walk(ast.parse(raw)):
    modules=[node.module]if isinstance(node,ast.ImportFrom)else[a.name for a in node.names]if isinstance(node,ast.Import)else[]
    for module in modules:
     if module and module.startswith('pg'):self.assertTrue(module+'.py'in files,(name,module))
  self.assertNotIn('history_configuration',files['pg894_bootstrap_existing.py'])
 def test_v2_new_only_and_dependency_closure(self):
  import pg894_sources_v2 as v2
  values=v2.files('a'*64)
  self.assertIn('pg894-bootstrap-tools-v2',values['Pg894BootstrapExisting.java'])
  self.assertNotIn('pg894-bootstrap-tools-v1',values['Pg894BootstrapExisting.java'])
  self.assertIn('"-v2"',values['Pg894BootstrapExisting.java'])
  self.assertIn("'-v2'",values['pg894_bootstrap_existing.py'])
  self.assertTrue(values['pg894_exec_record.py'].startswith('import re\n'))
  for name,raw in values.items():
   if not name.endswith('.py'):continue
   for node in ast.walk(ast.parse(raw)):
    modules=[node.module]if isinstance(node,ast.ImportFrom)else[a.name for a in node.names]if isinstance(node,ast.Import)else[]
    for module in modules:
     if module and module.startswith('pg'):self.assertTrue(module+'.py'in values,(name,module))
if __name__=='__main__':unittest.main()
