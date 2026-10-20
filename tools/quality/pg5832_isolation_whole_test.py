import ast
import unittest
import pg5832_isolation_whole as target


class CoherentIsolationWholeTest(unittest.TestCase):
    def test_exact_current_inventory_paths_and_unmodified_gate_profile(self):
        raw=target.server_source(target.SOURCE,'a'*64)
        constants=[n.value for n in ast.walk(ast.parse(raw))if isinstance(n,ast.Constant)]
        for n in(3967,590,1666):self.assertIn(n,constants)
        for n in(3955,587,1665):self.assertNotIn(n,constants)
        self.assertIn('source-full-PG5832',raw);self.assertNotIn('PG5808',raw)
        self.assertNotIn('failIfNoTests=false',raw)
        commands=[[n.value for n in node.elts if isinstance(n,ast.Constant)]for node in ast.walk(ast.parse(raw))if isinstance(node,ast.List)]
        checks=[v for v in commands if 'spotless:check'in v and '-o'in v]
        self.assertEqual(1,len(checks));self.assertLess(checks[0].index('spotless:check'),checks[0].index('test-compile'))

    def test_driver_declares_new_run_and_retains_unaccepted_native(self):
        raw=target.driver_source({})
        self.assertIn("'tests': 3967, 'suites': 590, 'mainClasses': 1666",raw)
        self.assertIn('pg5832-isolation-six-v1',raw);self.assertNotIn('pg5808',raw)
        self.assertIn('no old PT/native',raw)
        self.assertEqual(3,len(target.NEW_TESTS));self.assertEqual(4,len(target.CHANGED_TESTS))


if __name__=='__main__':unittest.main()
