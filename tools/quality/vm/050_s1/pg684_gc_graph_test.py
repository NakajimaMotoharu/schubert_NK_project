"""Execute exact extracted GC functions with independent literal suite and missing deps."""
import ast
from pathlib import Path
import unittest
from pg535_bootstrap_contract import UNIT, normal20
from pg535_bootstrap_contract_test import literal20
from pg536_bootstrap_execution_contract import record
import pg537_bootstrap_gc_contract_test as oracle
from pg684_completed_baseline_v2 import source

R = Path(__file__).resolve().parent


def graph():
    functions = [n for n in ast.parse((R/'pg537_bootstrap_gc_contract.py').read_text()).body if isinstance(n, ast.FunctionDef)]
    env = {'UNIT': UNIT, 'normal20': normal20, 'record': record}
    exec(compile(ast.Module(body=functions, type_ignores=[]), '<exactGC functions>', 'exec'), env)
    return env


class GraphTest(unittest.TestCase):
    def test_exact_extracted_functions_against_all_independent_gc_vectors(self):
        env = graph()
        for name in ('current_gc_after_known20', 'configuration_after_gc', 'unchanged_after_gc'):
            setattr(oracle, name, env[name])
        result = unittest.TestResult()
        unittest.defaultTestLoader.loadTestsFromTestCase(oracle.GcTest).run(result)
        self.assertEqual(2, result.testsRun)
        self.assertEqual([], result.failures)
        self.assertEqual([], result.errors)
        self.assertEqual([], result.skipped)

    def test_each_missing_dependency_reproduces_failure_not_success(self):
        env = graph(); del env['normal20']
        with self.assertRaises(NameError): env['current_gc_after_known20'](literal20(), {})
        env = graph(); del env['record']
        previous = {'ExecStart': '{ path=/usr/bin/java ; argv[]=/usr/bin/java fixed BootstrapAdminMain ; ignore_errors=no ; start_time=[START] ; stop_time=[END] ; pid=42 ; code=exited ; status=20 }'}
        current = {'ExecStart': previous['ExecStart']}
        actor = {'pid': '42', 'ticks': '123', 'invocation': 'a'*32, 'zeroCapabilities': True}
        with self.assertRaises(NameError): env['configuration_after_gc'](previous, current, actor)

    def test_new_payload_imports_only_verified_current_tools(self):
        raw = source(); tree = ast.parse(raw)
        payload = ast.literal_eval(next(n for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'PAYLOAD' for t in n.targets)).value)
        self.assertIn('pg684-completed-baseline-v2', payload)
        self.assertIn('from pg535_bootstrap_contract import UNIT,normal20', payload)
        self.assertIn('from pg536_bootstrap_execution_contract import record', payload)
        self.assertLess(payload.index('for name,digest in deps.items()'), payload.index('from pg535'))
        compile(payload, '<pinned readonly21 guest>', 'exec')


if __name__ == '__main__':
    unittest.main()
