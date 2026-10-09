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
 def test_all_generated_undefined_globals_zero(self):
  import sys
  sys.path.insert(0,'/home/mini/codex/project1/work/toolchain/pyflakes-3.4.0/runtime')
  from pyflakes.checker import Checker
  from pyflakes.messages import UndefinedName
  for name,raw in p.files('a'*64).items():
   if name.endswith('.py'):
    issues=[m.message_args[0]for m in Checker(ast.parse(raw),filename=name).messages if isinstance(m,UndefinedName)]
    self.assertEqual([],issues,name)
 def test_extracted_database_functions_actual_normal_negative(self):
  import stat
  env={};exec(compile(p.files('a'*64)['pg894_db_contract.py'],'<pure db>','exec'),env)
  normal={n:{'metadata':[1,2,0,0,stat.S_IFDIR|(0o755 if n=='runtime-parent'else 0o700),2,0,0,0],'entries':[],'xattrs':[]}for n in ('backup-request','cleanup-request','expiry-request','runtime-parent')}
  self.assertTrue(env['namespace_valid'](normal))
  for value in (None,{},[],{**normal,'foreign':{}}, {**normal,'backup-request':{'metadata':None,'entries':[],'xattrs':[]}}):self.assertFalse(env['namespace_valid'](value))
  for name in normal:
   for field,value in (('entries',['foreign']),('xattrs',['user.foreign']),('metadata',[0]*9)):
    changed={**normal,name:{**normal[name],field:value}};self.assertFalse(env['namespace_valid'](changed))
  for backend in (None,True,0,1,2147483648):
   with self.assertRaises(ValueError):env['peer_query'](backend)
  self.assertIn("application_name='PG894-bootstrap-guard'",env['peer_query'](123))
  self.assertTrue(env['peer_counts_valid'](True,[b'1',b'1',b'0',b'1']))
  self.assertTrue(env['peer_counts_valid'](False,[b'0']*4))
  for present,lines in ((None,[b'0']*4),(False,[b'1']*4),(True,None),(True,[])):self.assertFalse(env['peer_counts_valid'](present,lines))
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
