"""Current literal finite delta, parent binding and actual imports; no VM action."""
import ast
import builtins
import sys
import types
import unittest
from pathlib import Path
import pg717_sources as p

R = Path(__file__).resolve().parent


class Test(unittest.TestCase):
    def test_literal_all21_delta_and_each_mutation(self):
        module = types.ModuleType('pg717_completed_contract')
        exec(compile(p.contract(), '<pure finite21>', 'exec'), module.__dict__)
        sys.modules[module.__name__] = module
        raw = p.bind((R / 'pg685_contract_graph_test.py').read_text())
        # Reuse only the old independent four-vector class body, not old operations.
        raw_oracle = p.bind(p.previous.bind((R / 'pg624_completed_contract_test.py').read_text()))
        raw_oracle = raw_oracle.replace("b'activation_id=970bbce1',b'activation_id=870bbce1'", "b'activation_id=c6815985',b'activation_id=d6815985'")
        raw_oracle = raw_oracle.replace("'bootstrapTools','caddyPre')", "'bootstrapTools','caddyPre','namespace','currentBootstrapProofs')")
        env = {'__name__': 'literal_new_oracle'}; exec(compile(raw_oracle, '<independent21>', 'exec'), env)
        result = unittest.TestResult(); unittest.defaultTestLoader.loadTestsFromTestCase(env['ContractTest']).run(result)
        self.assertEqual(result.testsRun, 4); self.assertEqual(result.failures, []); self.assertEqual(result.errors, [])
        self.assertIn('currentBootstrapProofs', raw)

    def test_current_genuine_parent_and_cli_preserve_old_dependencies(self):
        raw = p.refs(); ast.parse(raw)
        for literal in ('58154dc72379fc8a15c1d3098f75b571e14968819bec6901dfff594a6c78c029',
                        '121040711116', 'pg702-bootstrap-existing-v1', 'pg664-bootstrap-existing-v1', 'len(value)==21'):
            self.assertIn(literal, raw)
        self.assertIn('configure("PG682","9bd50536f692610036a0ed8b83e0a8b35fe2a66f",OLD)', p.java())
        self.assertIn('configure("PG715",source,NEXT)', p.java())
        self.assertIn("JOB='122726'", p.receipt())
        self.assertIn('pg464-code-tools-v2', p.compile_script())
        self.assertIn('pg481-pending-tools-v2', p.compile_script())
        self.assertIn('pg680-owner-six-host-v1', p.compile_script())

    def test_real_inert_import_graph_and_each_dependency_refusal(self):
        module = types.ModuleType('pg717_completed_contract'); exec(compile(p.contract(), '<pure contract>', 'exec'), module.__dict__)
        sys.modules[module.__name__] = module
        prior = sys.modules.get('dbus'); original = builtins.__import__; sys.modules['dbus'] = types.ModuleType('dbus')
        try:
            env = {'__name__': 'inert', '__file__': str(R / 'pg717_completed_refs.py')}
            exec(compile(p.refs(), '<actual imports>', 'exec'), env); self.assertTrue(callable(env['main']))
            self.assertEqual(env['OLD'], '/opt/schubert-nk/releases/0.1.0-PG682')
            for missing in ('pg717_completed_contract', 'pg604_unit_sources'):
                def deny(name, globals=None, locals=None, fromlist=(), level=0):
                    if name == missing: raise ModuleNotFoundError('missing required helper')
                    return original(name, globals, locals, fromlist, level)
                bad = {**env, '__builtins__': {**vars(builtins), '__import__': deny}}
                with self.subTest(missing=missing), self.assertRaises(ModuleNotFoundError): exec(compile(p.refs(), '<missing dependency>', 'exec'), bad)
        finally:
            if prior is None: sys.modules.pop('dbus', None)
            else: sys.modules['dbus'] = prior


if __name__ == '__main__': unittest.main()
