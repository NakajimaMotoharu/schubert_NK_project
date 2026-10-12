import ast
import unittest
from pg1527_filesystem_selected_retry import server

class NoMissingSuiteSuccessTest(unittest.TestCase):
 def test_exact_required_predicate_excludes_compile_only_modules(self):
  t=ast.parse(server());assign={n.targets[0].id:n.value for n in t.body if isinstance(n,ast.Assign)and isinstance(n.targets[0],ast.Name)}
  expected=ast.literal_eval(assign['EXPECTED']);self.assertEqual(7,len(expected));self.assertEqual(101,sum(expected.values()))
  predicate=ast.Expression(assign['passed']);code=compile(ast.fix_missing_locations(predicate),'<independent actual selected admission>','eval')
  class Result: returncode=0
  results={n:{'tests':count,'failures':0,'errors':0,'skipped':0,'freshAfterBegin':True}for n,count in expected.items()}
  env={'r':Result(),'results':results,'EXPECTED':expected,'static':{'protocol':0,'storage':0,'bootstrap':0,'batch':0},'inputs':{}}
  self.assertTrue(eval(code,env))
  for name in expected:
   removed=results.pop(name);self.assertFalse(eval(code,env));results[name]=removed
   for field,bad in [('tests',0),('tests',removed['tests']+1),('failures',1),('errors',1),('skipped',1),('freshAfterBegin',False)]:
    value=removed[field];removed[field]=bad;self.assertFalse(eval(code,env));removed[field]=value
  self.assertTrue('compileOnlyUnselectedNotPtPass' in server())
if __name__=='__main__':unittest.main()
