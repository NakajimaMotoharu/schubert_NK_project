import ast
import unittest
from pg1521_profile_pair_once_handoff import payload

class OnceHandoffTest(unittest.TestCase):
 def test_exact_order_reap_and_no_resignal(self):
  tree=ast.parse(payload());calls=[n for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=='terminate_once']
  self.assertEqual([98452,98426],[n.args[0].value for n in calls])
  functions={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
  waits=functions['wait_reaped'];self.assertTrue(any(isinstance(n,ast.While)for n in ast.walk(waits)))
  self.assertFalse(any(isinstance(n,ast.Attribute)and n.attr in {'pidfd_send_signal','terminate_once'}for n in ast.walk(waits)))
  self.assertIn('time.monotonic() < deadline',ast.unparse(waits))
  self.assertIn('== ticks',ast.unparse(waits))
  parentcalls=[n for n in tree.body if isinstance(n,ast.Expr)and isinstance(n.value,ast.Call)and isinstance(n.value.func,ast.Name)]
  names=[n.value.func.id for n in parentcalls];self.assertEqual(2,names.count('wait_reaped'))
if __name__=='__main__':unittest.main()
