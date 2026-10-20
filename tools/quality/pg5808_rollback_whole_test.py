import ast
import unittest
import pg5808_rollback_whole as target


class CoherentRollback3955Test(unittest.TestCase):
    def test_new_fixed_counts_paths_and_no_held_operation(self):
        raw=target.server_source(target.SOURCE,'a'*64);constants=[n.value for n in ast.walk(ast.parse(raw))if isinstance(n,ast.Constant)]
        self.assertIn(3955,constants);self.assertIn(587,constants);self.assertIn(1665,constants)
        self.assertNotIn(3939,constants);self.assertNotIn(1664,constants)
        self.assertNotIn('PG5780',raw);self.assertIn('source-full-PG5808',raw)
        lists=[[n.value for n in node.elts if isinstance(n,ast.Constant)and isinstance(n.value,str)]for node in ast.walk(ast.parse(raw))if isinstance(node,ast.List)]
        commands=[values for values in lists if 'spotless:check'in values and '-o'in values]
        self.assertEqual(1,len(commands));self.assertLess(commands[0].index('spotless:check'),commands[0].index('test-compile'))
        self.assertNotIn('failIfNoTests=false',raw)

    def test_driver_declares_exact_test_scope_without_old_success_import(self):
        raw=target.driver_source({})
        self.assertIn("'tests': 3955, 'suites': 587, 'mainClasses': 1665",raw)
        self.assertIn('pg5808-rollback-six-v1',raw)
        self.assertNotIn('pg5780',raw);self.assertNotIn('PG5780',raw)
        self.assertEqual(4,len(target.NEW_TESTS));self.assertEqual(4,len(target.CHANGED_TESTS))


if __name__=='__main__':unittest.main()
