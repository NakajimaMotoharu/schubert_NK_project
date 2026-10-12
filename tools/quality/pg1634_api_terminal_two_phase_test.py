"""BUG1141/YKT909: distinct real goals/private cache and mandatory API13 outcome."""
import ast
import unittest
import pg1634_api_terminal_two_phase as p


class TwoPhaseSelectionTest(unittest.TestCase):
    def test_dependencies_have_no_test_goal_and_api_keeps_exact_tests(self):
        tree=ast.parse(p.server());assignments={n.targets[0].id:n.value for n in tree.body if isinstance(n,ast.Assign)and isinstance(n.targets[0],ast.Name)}
        values=lambda key:[n.value for n in assignments[key].right.elts if isinstance(n,ast.Constant)]
        dependencies=values('dependency_args');api=values('api_args')
        self.assertNotIn('test',dependencies);self.assertNotIn('verify',dependencies)
        self.assertIn('test-compile',dependencies);self.assertIn('jar:test-jar',dependencies);self.assertIn('install:install',dependencies)
        self.assertIn('test',api);self.assertIn('src/schubert-nk-api',api)
        self.assertNotIn('-DfailIfNoTests=false',api)
        self.assertEqual({'ApiProcessMainTest':4,'ApiProcessLifetimeTest':4,'ApiTerminalCaptureTest':3,'ApiCommittedFatalBindingTest':2},ast.literal_eval(assignments['EXPECTED']))
        gate=ast.unparse(assignments['passed'])
        self.assertIn('dependency.returncode == 0',gate);self.assertIn('cache_unchanged',gate)
        self.assertIn('set(results) == set(EXPECTED)',gate)
        self.assertIn("v['tests'] == EXPECTED[n]",gate)
        self.assertIn("v['failures'] == v['errors'] == v['skipped'] == 0",gate)
        self.assertTrue(any(isinstance(n,ast.Assign)and isinstance(n.targets[0],ast.Name)and n.targets[0].id=='args'and 'private_repo' in ast.unparse(n.value)and '-Dmaven.repo.local=' in ast.unparse(n.value)for n in tree.body))


if __name__=='__main__':unittest.main()
