"""SSC233 independent legacy oracle retargeted to literal current cohort; no VM action."""
import ast
import sys
import types
import unittest
from pathlib import Path
import pg685_sources as p

R = Path(__file__).resolve().parent


def module(name, source):
    obj = types.ModuleType(name); obj.__file__ = str(R/(name+'.py'))
    sys.modules[name] = obj
    exec(compile(source, '<current fixed pure helper>', 'exec'), obj.__dict__)
    return obj


class CurrentGraphTest(unittest.TestCase):
    def test_full21_literal_finite_delta_and_each_mutation(self):
        module('pg685_completed_contract', p.contract())
        raw = p.bind((R/'pg624_completed_contract_test.py').read_text())
        raw = raw.replace("b'activation_id=970bbce1',b'activation_id=870bbce1'",
                          "b'activation_id=ad15ac4a',b'activation_id=bd15ac4a'")
        raw = raw.replace("'bootstrapTools','caddyPre')", "'bootstrapTools','caddyPre','namespace','currentBootstrapProofs')")
        self.assertIn("'namespace','currentBootstrapProofs'", raw)
        env = {'__name__': 'literal_current_oracle'}
        exec(compile(raw, '<independent completed21 literal oracle>', 'exec'), env)
        result = unittest.TestResult()
        unittest.defaultTestLoader.loadTestsFromTestCase(env['ContractTest']).run(result)
        self.assertEqual(4, result.testsRun)
        self.assertEqual([], result.failures); self.assertEqual([], result.errors)

    def test_generated_refs_globals_and_current_source_fields(self):
        raw = p.refs(); tree = ast.parse(raw)
        for literal in ('c039e70561fd7e5bab3ecf5ce204462d8415f4022d13793711c338a64d2f663d',
                        "baseline['parentPid1']", '109694780700', "len(value)==21", 'currentBootstrapProofs', 'namespace'):
            self.assertIn(literal, raw)
        self.assertNotIn("baseline['pid1']", raw)
        self.assertIn("'sys':sys", raw)
        self.assertIn("'require':require", raw)
        self.assertTrue(any(isinstance(n, ast.ImportFrom) and n.module == 'pg685_completed_contract' for n in tree.body))
        self.assertIn("'PG685-completed-codeonly'", raw)
        for obsolete in ('pg624', 'Pg624', '3a53b979', '970bbce1', '==492'):
            self.assertNotIn(obsolete, raw)

    def test_actual_receipt_bindings_and_no_old_source_authority(self):
        raw = p.receipt(); self.assertIn("JOB='111752'", raw)
        self.assertIn('START=107901545407', raw)
        self.assertIn("RUN='601297d0-a8ba-47da-852b-0ffeae409965'", raw)
        compile(raw, '<fixed current receipt>', 'exec')
        java = p.java()
        self.assertIn('configure("PG631","36fe7a0b938489d61d17d49c1c30a6fbbef699d5",OLD)', java)
        self.assertIn('configure("PG682",source,NEXT)', java)
        self.assertIn('phase="DATABASE_CLOSE";database.rollback();database.close();phase="REFERENCE_CLOSE";refs.release()', java)
        self.assertNotIn('PG600', java); self.assertNotIn('PG621', java)
        self.assertIn(p.SOURCE, java); self.assertIn(p.DIGEST, java)


if __name__ == '__main__':
    unittest.main()
