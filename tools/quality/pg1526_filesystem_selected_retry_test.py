import ast
import unittest
from pg1526_filesystem_selected_retry import server

class ClosedReactorTest(unittest.TestCase):
 def test_modules_offline_no_parent_unselected_not_passed(self):
  t=ast.parse(server());assign={n.targets[0].id:n.value for n in t.body if isinstance(n,ast.Assign)and isinstance(n.targets[0],ast.Name)}
  self.assertEqual(['protocol','storage','bootstrap','batch'],ast.literal_eval(assign['MODULES']))
  self.assertEqual(101,sum(ast.literal_eval(assign['EXPECTED']).values()))
  args=assign['args'];constants=[n.value for n in ast.walk(args)if isinstance(n,ast.Constant)]
  self.assertIn('-o',constants);self.assertNotIn('-am',constants)
  self.assertIn('spotless:check',constants);self.assertIn('spotbugs:check',constants)
  self.assertTrue('compileOnlyUnselectedNotPtPass' in server())
if __name__=='__main__':unittest.main()
