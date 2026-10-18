"""Same actual a2ecc generation and independent newday raw-first acceptance guards."""
import ast
import copy
import json
import types
import unittest
from pyflakes.api import check, checkPath
import pg5036_current_admission_image as admission
import pg5038_current_genuine_terminal as terminal
import pg5040_current_newday_rows as rows
import pg5042_current_newday_whole_seal as seal


def constants(raw):
    return {t.id: ast.literal_eval(n.value) for n in ast.parse(raw).body if isinstance(n, ast.Assign)
            for t in n.targets if isinstance(t, ast.Name) and t.id in {'ORACLE', 'GUARD'}}


class Acceptance(unittest.TestCase):
    def test_actual_generation_full11_source_before80_never_old_credit(self):
        observed = admission.live()
        raw = admission.payload(observed)
        self.assertEqual(0, check(raw, '<actual current before>'))
        for text in (admission.SOURCE, admission.BOM, admission.ONCE, admission.PUBLICATION,
                     admission.PUBLICATION_PATH, "'nativeExecEntries':80", '!=80', observed['run'], observed['activation']):
            self.assertIn(text, raw)
        self.assertNotIn(admission.previous.SOURCE, raw)
        self.assertNotIn(admission.previous.ONCE, raw)
        self.assertNotIn('systemctl', raw)

    def test_lossless_projection_foreign_null_and_nonquiescent_rejected(self):
        units = {str(i): {'MainPID': '0', 'ControlPID': '0', 'Job': ''} for i in range(10)}
        value = {'backup': {'literal': ['independent']}, 'configuration': {n: {} for n in units},
                 'extraDurable': {'credentials': {}, 'oldProofs': {}}, 'originals': {'literal': ['before']},
                 'pid1': {}, 'rows': {str(i): [] for i in range(24)}, 'runtime': {}, 'startup': {},
                 'unitFilesActual': {'literal': ['independent']}, 'units': units,
                 'native': {str(i) + '.exec': {} for i in range(80)}}
        publication = {'unitFilesActual': copy.deepcopy(value['unitFilesActual'])}
        before = copy.deepcopy(value)
        projected = admission.project(value, publication)
        self.assertEqual(before, value)
        self.assertEqual(value['native'], projected['native'])
        self.assertEqual({'originals': value['originals'], 'backup': value['backup'],
                          **value['extraDurable']}, projected['durable'])
        for change in (lambda v: v.pop('rows'), lambda v: v.update(database={}), lambda v: v.update(rows=None),
                       lambda v: v['native'].pop('0.exec'), lambda v: v['units']['0'].update(MainPID='2'),
                       lambda v: v.update(extraDurable={})):
            bad = copy.deepcopy(value)
            change(bad)
            with self.assertRaises(ValueError):
                admission.project(bad, publication)
        with self.assertRaises(ValueError):
            admission.project(None, publication)
        with self.assertRaises(ValueError):
            admission.project(value, {'unitFilesActual': {}})

    def test_genuine_terminal_exact_current_run_pid1_and_original_budget(self):
        observed = admission.live()
        raw = terminal.payload(observed)
        self.assertEqual(0, check(raw, '<actual genuine terminal>'))
        for text in (admission.SOURCE, admission.BOM, terminal.TERM, observed['invocation'], observed['run'],
                     "'_PID=1'", '1800', 'genuineRootDone'):
            self.assertIn(text, raw)
        self.assertNotIn('pg4890-parent-watch-v1', raw)
        self.assertNotIn('pg4902-current-genuine-terminal-v1', raw)
        self.assertNotIn('-parent-watch-v1', raw)  # PID1/DONE proof is independent of observer output.

    def test_raw24_saved_before_parse_newday_session_and_crypto_oracle(self):
        raw = rows.payload(admission.live(), 'a' * 64)
        self.assertEqual(0, check(raw, '<pure source all24>'))
        self.assertLess(raw.index("preserve('sql-stdout.private.jsonl'"), raw.index('for line in r.stdout.splitlines():'))
        self.assertLess(raw.index("preserve('after.private.json'"), raw.index('result=qualify_current(before,now,'))
        self.assertIn("before=json.loads(br)['rows']", raw)
        self.assertIn('inbox=expected_inbox(before,expected)', raw)
        self.assertIn('NKQRY1', raw)
        self.assertIn('def qualify_new_day', raw)
        self.assertNotIn('require(all(history.values()))', raw)
        self.assertIn("KEY[:]=b'\\0'*len(KEY)", raw)

    def test_whole_guard_oracle_current80_and_raw_first_exactly_once(self):
        observed = admission.live()
        raw = seal.payload(observed, 'a' * 64)
        self.assertEqual(0, check(raw, '<pure whole emission>'))
        values = constants(raw)
        self.assertEqual({'ORACLE', 'GUARD'}, set(values))
        self.assertIn('def qualify_new_day', values['ORACLE'])
        self.assertIn('def expected_inbox', values['ORACLE'])
        self.assertIn("KEY[:]=b'\\0'*len(KEY)", values['ORACLE'])
        self.assertNotIn('require(all(history.values()))', values['ORACLE'])
        genuine = terminal.payload(observed)
        marker = "out=pathlib.Path('/var/lib/pgpt-s1-preservation/" + terminal.TERM + "')"
        self.assertEqual(genuine[:genuine.index(marker)], values['GUARD'])
        self.assertIn('1800', values['GUARD'])
        self.assertIn('genuineRootDone', values['GUARD'])
        self.assertIn(seal.SLOT + '-raw', raw)
        self.assertIn(admission.ONCE + '/before.private.json', raw)
        self.assertIn(admission.PUBLICATION_PATH, raw)
        self.assertIn('/opt/schubert-nk/releases/0.1.0-PG4980', raw)
        self.assertIn('pg4980-manifest.sig', raw)
        self.assertNotIn('/opt/schubert-nk/releases/0.1.0-PG4860', raw)
        self.assertEqual(1, raw.count('def preserve_raw('))
        self.assertEqual(1, raw.count('def strict_equal('))
        self.assertLess(raw.index("preserve_raw('captured-'"), raw.index(" business=types.ModuleType('independent_sql')"))

    def test_actual_sql_bytes_preserved_on_parse_failure(self):
        tree = ast.parse(seal.payload(admission.live(), 'a' * 64))
        capture = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'capture')
        index = next(i for i, n in enumerate(capture.body) if isinstance(n, ast.Assign)
                     and any(isinstance(t, ast.Name) and t.id == 'sql_raw' for t in n.targets))
        block = ast.Module(body=capture.body[index:index + 3], type_ignores=[])
        saved = []
        ns = {'command': lambda args, bound: b'not JSON\n', 'sql': 'independent SQL',
              'time': types.SimpleNamespace(monotonic_ns=lambda: 123),
              'preserve_raw': lambda label, data: saved.append((label, data)), 'rs': {}, 'json': json}
        with self.assertRaises(json.JSONDecodeError):
            exec(compile(block, '<actual SQL preserve before parse>', 'exec'), ns)
        self.assertEqual([('sql-123', b'not JSON\n')], saved)

    def test_unequal_full_snapshots_saved_and_bool_not_int(self):
        tree = ast.parse(seal.payload(admission.live(), 'a' * 64))
        helper = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'strict_equal')
        ns = {}
        exec(compile(ast.Module(body=[helper], type_ignores=[]), '<strict full image>', 'exec'), ns)
        self.assertFalse(ns['strict_equal']({'counter': True}, {'counter': 1}))
        self.assertFalse(ns['strict_equal']({'counter': None}, {'counter': 0}))
        self.assertTrue(ns['strict_equal']({'rows': [1]}, {'rows': [1]}))
        matches = [(n.body, i) for n in ast.walk(tree) if isinstance(n, ast.Try)
                   for i, x in enumerate(n.body) if isinstance(x, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == 'current' for t in x.targets)
                   and isinstance(x.value, ast.Call) and isinstance(x.value.func, ast.Name)
                   and x.value.func.id == 'capture']
        self.assertEqual(1, len(matches))
        body, index = matches[0]
        end = next(i for i in range(index, len(body)) if isinstance(body[i], ast.Expr)
                   and isinstance(body[i].value, ast.Call) and isinstance(body[i].value.func, ast.Name)
                   and body[i].value.func.id == 'require')
        observations, saved = iter([{'literal': 1}, {'literal': 2}]), []
        def require(value):
            if not value:
                raise ValueError('full mismatch')
        ns.update(capture=lambda: next(observations), preserve_raw=lambda label, data: saved.append((label, json.loads(data))),
                  json=json, require=require)
        with self.assertRaises(ValueError):
            exec(compile(ast.Module(body=body[index:end + 1], type_ignores=[]), '<actual full compare>', 'exec'), ns)
        self.assertEqual([('complete-first', {'literal': 1}), ('complete-second', {'literal': 2})], saved)

    def test_all_host_sources_static0(self):
        for p in (admission.__file__, terminal.__file__, rows.__file__, seal.__file__, __file__):
            self.assertEqual(0, checkPath(p))


if __name__ == '__main__':
    unittest.main()
