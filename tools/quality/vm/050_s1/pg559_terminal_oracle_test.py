"""Current full rows, bound receipt, action/output inventory; no VM or Production expected."""
import ast,copy,pathlib,stat,unittest
import pg556_parent_receipt_test as receipt
R=pathlib.Path(__file__).parent
source=ast.parse((R/'pg559_terminal_refs.py').read_text());env={'stat':stat}
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef)and n.name in ('require','same_rows','same_value','peer_query','peer_counts_valid','namespace_valid')],type_ignores=[]),'<independent preservation>','exec'),env)
class RowsTests(unittest.TestCase):
 def test_exact_all_columns_and_types(self):
  before={str(n):[{'id':n,'independent':{'status':'literal','flag':False,'count':0}}]for n in range(24)}
  self.assertTrue(env['same_rows'](before,copy.deepcopy(before)))
  for bad in (None,[],{},dict(before,foreign=[])):
   self.assertFalse(env['same_rows'](before,bad))
  for k in before:
   for replacement in (None,{},[],[{'id':99}],before[k]*2):
    bad=copy.deepcopy(before);bad[k]=replacement;self.assertFalse(env['same_rows'](before,bad))
   for name,new in [('status',None),('flag',0),('count',False),('count',1)]:
    bad=copy.deepcopy(before);bad[k][0]['independent'][name]=new;self.assertFalse(env['same_rows'](before,bad))
 def test_current_source_actions_outputs(self):
  java=(R/'Pg559TerminalReadback.java').read_text();helper=(R/'pg559_terminal_refs.py').read_text();compile_script=(R/'pg559_terminal_compile_v1.sh').read_text()
  for s in (java,helper):
   for wrong in ('PG495','33502','561260','old452RowsNewTenSkipVerified'):
    self.assertNotIn(wrong,s)
  self.assertNotIn('refs.check("stop:',java);self.assertNotIn('MaintenanceUnit.values()',java)
  self.assertIn('require("before".equals(name));',java)
  self.assertIn('db.rollback();db.close();phase="REF_CLOSE";refs.release();',java)
  self.assertIn('allNewScopesReturnedNormally=true',java)
  self.assertIn('set -euC',compile_script)
  for line in compile_script.splitlines():
   if ' > 'in line:self.assertIn('pg559-',line)
  self.assertIn('pg498-pending-tools-v3',compile_script);self.assertIn('pg481-pending-tools-v2',compile_script)
  self.assertIn('Pg559TerminalReadback',helper);self.assertIn("'strict','owner'",helper)
  driver=(R/'pg559_terminal_native_v2.py').read_text();v2compile=(R/'pg559_terminal_compile_v2.sh').read_text()
  for role in ('tools','readback'):
   self.assertIn('pg559-terminal-'+role+'-v2',java)
  self.assertIn('pg559-terminal-readback-v2',helper)
  for suffix in ('tools','stage','native','compile','oracle'):
   self.assertIn('pg559-terminal-'+suffix+'-v2',driver)
  for text in (driver,v2compile):
   for external in ('pg498-pending-tools-v2','pg498-pending-tools-v3'):
    if external in text:self.assertNotIn(external.replace('-v2','-v1').replace('-v3','-v1'),text)
  self.assertIn('assert len(files)==5',driver);self.assertIn("'Ran 6 tests'",driver)
  self.assertIn("'run':'PG559-terminal-readback-v2'",driver)
  self.assertNotIn('PG559-terminal-readback-v1',driver)
 def test_peer_sql_and_release(self):
  for bad in (None,True,False,0,1,-1,2147483648,'77',77.0):
   with self.assertRaises(ValueError):env['peer_query'](bad)
  query=env['peer_query'](77)
  self.assertIn("a.pid=77 and a.usename='schubert_batch'",query);self.assertNotIn('77and',query)
  self.assertIn('where pid=77;',query);self.assertIn('pid not in (77,pg_backend_pid())',query);self.assertIn("backend_type='client backend'",query)
  self.assertEqual(query.count(';'),4)
  for present,good in [(True,[b'1',b'1',b'0',b'1']),(False,[b'0']*4)]:
   self.assertTrue(env['peer_counts_valid'](present,good))
   for bad in (None,{},good[:-1],good+[b'0'],[int(x)for x in good],['0']*4):self.assertFalse(env['peer_counts_valid'](present,bad))
   for n in range(4):
    bad=good.copy();bad[n]=b'9';self.assertFalse(env['peer_counts_valid'](present,bad))
  self.assertFalse(env['peer_counts_valid'](False,[b'1',b'0',b'0',b'0']))
  self.assertFalse(env['peer_counts_valid'](None,[b'0']*4))
 def test_namespace_contract(self):
  value={n:{'metadata':[28,200,0,0,stat.S_IFDIR|(0o755 if n=='runtime-parent'else 0o700),2,40,100,100],'entries':[],'xattrs':[]}for n in ('backup-request','cleanup-request','expiry-request','runtime-parent')}
  self.assertTrue(env['namespace_valid'](value))
  for bad in (None,{},dict(value,foreign={})):
   self.assertFalse(env['namespace_valid'](bad))
  for n in value:
   for k,v in [('entries',['foreign']),('entries',None),('xattrs',['system.posix_acl_access']),('metadata',None)]:
    bad=copy.deepcopy(value);bad[n][k]=v;self.assertFalse(env['namespace_valid'](bad))
   for idx,replacement in [(1,0),(2,1),(3,1),(4,stat.S_IFLNK|0o700),(4,stat.S_IFDIR|0o777),(0,True),(7,None)]:
    bad=copy.deepcopy(value);bad[n]['metadata'][idx]=replacement;self.assertFalse(env['namespace_valid'](bad))
  helper=(R/'pg559_terminal_refs.py').read_text();self.assertIn('os.path.lexists',helper);self.assertIn('os.O_DIRECTORY|os.O_NOFOLLOW',helper)
def load_tests(loader,tests,pattern):
 tests.addTests(loader.loadTestsFromTestCase(receipt.Test));return tests
if __name__=='__main__':unittest.main()
