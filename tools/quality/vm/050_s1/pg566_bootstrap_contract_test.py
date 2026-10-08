"""Source assembly/namespace/typed-peer/history guarantees before actual guest scopes."""
import ast
from pathlib import Path
import unittest
from pg559_terminal_refs import peer_query, peer_counts_valid
from pg536_bootstrap_execution_contract import configuration


class Test(unittest.TestCase):
    def test_sealed_owner_namespace_is_complete_and_no_old_globals_patch(self):
        source = Path(__file__).with_name('pg566_bootstrap_existing.py').read_text()
        tree = ast.parse(source)
        function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'main')
        sealed = next(n.value for n in ast.walk(function) if isinstance(n, ast.Assign)
                      and any(isinstance(t, ast.Name) and t.id == 'sealed' for t in n.targets))
        self.assertEqual({key.value for key in sealed.keys},
                         {'datetime', 'hashlib', 'json', 'os', 'pathlib', 're', 'stat', 'subprocess',
                          'sys', 'time', 'require'})
        self.assertNotIn('globals()', source)
        self.assertNotIn('FIELDS', {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)
                                   and isinstance(n.ctx, ast.Load)})
        self.assertIn("state==('READY'if MODE=='verify'else'RETIRED')", source)
        self.assertIn("os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW", source)
        self.assertIn("history_configuration(previous,configuration[unit],terminal,actor", source)
        self.assertIn("namespace==baseline['namespace']", source)
        self.assertIn("require(data==baseline['rows'])", source)
        starts = [n for n in ast.walk(tree) if isinstance(n, ast.List)
                  and len(n.elts) >= 3 and all(isinstance(e, ast.Constant) for e in n.elts[:3])
                  and [e.value for e in n.elts[:3]] == ['/usr/bin/systemctl', 'start', '--no-block']]
        self.assertEqual(len(starts), 1)

    def test_typed_sql_and_all_four_counts_are_not_weakened(self):
        query = peer_query(42).replace('PG559-terminal-readback', 'PG566-bootstrap-guard')
        self.assertIn('pid=42 and ', query)
        self.assertIn("application_name='PG566-bootstrap-guard'", query)
        self.assertEqual(query.count('select count(*)'), 4)
        self.assertTrue(peer_counts_valid(True, [b'1', b'1', b'0', b'1']))
        self.assertTrue(peer_counts_valid(False, [b'0', b'0', b'0', b'0']))
        for counts in ([b'1', b'0', b'0', b'1'], [b'1', b'1', b'1', b'1'], [b'1', b'1', b'0', b'0']):
            self.assertFalse(peer_counts_valid(True, counts))
        for value in (True, 0, -1, '42', None):
            with self.assertRaises(ValueError): peer_query(value)

    def test_known_history_contract_remains_separate_from_declared_configuration(self):
        self.assertFalse(configuration(None, None, None, None, None, None))
        # Complete positive/negative literal history vectors remain in the existing independently
        # tested pg536 contract, included by the compile driver; no new lax regexp/normalization.
        java = Path(__file__).with_name('Pg566BootstrapExisting.java').read_text()
        self.assertIn('refs.check("run")', java)
        self.assertIn('if(MODE.equals("execute"))', java)
        self.assertIn('phase="PREPARE_DATABASE_SCOPE_CLOSE"', java)
        self.assertIn('phase="POST_DATABASE_SCOPE_CLOSE"', java)
        self.assertNotIn('PG495', java)
        self.assertNotIn('91a748b4', java)

    def test_current_compile_dependency_is_not_the_new_output_version(self):
        script = Path(__file__).with_name('pg566_bootstrap_compile_v3.sh').read_text()
        self.assertEqual(script.count('pg548-release-v1/'), 4)
        self.assertNotIn('pg548-release-v2', script)
        self.assertIn('pg566-bootstrap-tools-v3', script)
        driver = Path(__file__).with_name('pg566_bootstrap_native_v1.py').read_text()
        self.assertIn("CLASSDIR = W / 'pg566-bootstrap-tools-v3'", driver)
        self.assertIn("prior['actualExit'] == 0 and prior['toolHashes'] == hashes", driver)
        self.assertIn("assert not any(p.exists() for p in (log, exit_file, result_file))", driver)
        self.assertIn("log.open('xb')", driver)
        for label in ('pg566-bootstrap-tools-v2', 'pg548-release-v2', 'pg535-bootstrap-tools-v1'):
            self.assertNotIn(label, driver)


if __name__ == '__main__':
    unittest.main()
