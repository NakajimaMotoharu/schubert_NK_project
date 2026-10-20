import ast
import subprocess
import unittest
import pg5860_terminal_whole as target


class CoherentTerminalWholeTest(unittest.TestCase):
    def test_current_source_inventory_and_unchanged_gate_profile(self):
        actual=subprocess.check_output(['git','rev-parse','0f572da66'],cwd=target.ROOT,text=True).strip()
        self.assertEqual(actual,target.SOURCE)
        raw=target.server_source(target.SOURCE,'a'*64)
        constants=[n.value for n in ast.walk(ast.parse(raw))if isinstance(n,ast.Constant)]
        for n in(3971,592,1666):self.assertIn(n,constants)
        for n in(3967,590):self.assertNotIn(n,constants)
        self.assertIn('source-full-PG5860',raw);self.assertNotIn('PG5832',raw)
        self.assertNotIn('failIfNoTests=false',raw)
        commands=[[n.value for n in node.elts if isinstance(n,ast.Constant)]for node in ast.walk(ast.parse(raw))if isinstance(node,ast.List)]
        checks=[v for v in commands if 'spotless:check'in v and '-o'in v]
        self.assertEqual(1,len(checks));self.assertLess(checks[0].index('spotless:check'),checks[0].index('test-compile'))

    def test_driver_new_namespace_and_no_old_success_import(self):
        raw=target.driver_source({})
        self.assertIn("'tests': 3971, 'suites': 592, 'mainClasses': 1666",raw)
        self.assertIn('pg5860-terminal-six-v1',raw);self.assertNotIn('pg5832',raw)
        self.assertIn('no old PT/native import',raw)
        self.assertEqual(2,len(target.NEW_TESTS));self.assertEqual(6,len(target.CHANGED_TESTS))


if __name__=='__main__':unittest.main()
