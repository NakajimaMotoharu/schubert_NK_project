"""Current full rows, bound receipt, action/output inventory; no VM or Production expected."""
import ast,copy,pathlib,unittest
import pg556_parent_receipt_test as receipt
R=pathlib.Path(__file__).parent
source=ast.parse((R/'pg559_terminal_refs.py').read_text());env={}
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef)and n.name in ('same_rows','same_value')],type_ignores=[]),'<independent preservation>','exec'),env)
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
def load_tests(loader,tests,pattern):
 tests.addTests(loader.loadTestsFromTestCase(receipt.Test));return tests
if __name__=='__main__':unittest.main()
