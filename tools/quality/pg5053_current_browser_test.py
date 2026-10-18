"""Identity-only Browser invariants and exact newday Root/Browser chain preservation."""
import ast
import inspect
import unittest
from unittest.mock import patch
from pyflakes.api import check, checkPath
import pg5045_current_browser_socks as socks
import pg5036_current_admission_image as admission
import pg5042_current_newday_whole_seal as root
import pg5046_current_browser_ready as ready
import pg5048_current_same_owner_browser as actual
import pg5050_current_browser_composite as composite
import pg5052_current_parent_projection as projection


def literal(raw, name):
    return next(ast.literal_eval(n.value) for n in ast.parse(raw).body if isinstance(n, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == name for t in n.targets))


class Browser(unittest.TestCase):
    def test_identity_only_twelve_original_oracles_current_source(self):
        self.assertEqual(admission.SOURCE, ready.SOURCE)
        self.assertIn('tools/quality/pg5046_current_browser_ready.py', ready.PINNED)
        for name in ready.shared.JAVA_INPUTS:
            raw = (ready.shared.ROOT / name).read_text()
            if name not in ready.shared.SHARED:
                self.assertEqual(1, raw.count(ready.shared.OLD))
                changed = raw.replace(ready.shared.OLD, ready.SOURCE)
                self.assertEqual(raw, changed.replace(ready.SOURCE, ready.shared.OLD))
        self.assertIn("['plannedCases']==12", inspect.getsource(ready.shared.require_ready))

    def test_no_browser_without_current_genuine_receipt_and_owned_socket_proof(self):
        with patch.object(actual, 'receipt', side_effect=ValueError('current proof missing')):
            with self.assertRaisesRegex(ValueError, 'current proof missing'):
                actual.guard()
        body = inspect.getsource(actual.previous.previous.previous.main)
        self.assertLess(body.index('ready.require_ready()'), body.index('subprocess.run(command,'))
        new = inspect.getsource(actual.main)
        self.assertIn("raw.replace('previous.previous.owned_socks()', 'owned_socks()')", new)
        self.assertNotIn('owner.EXPECTED=', inspect.getsource(socks))

    def test_numeric_and_same_source_phase_receipt_only(self):
        fixture = {'actualExit': 0, 'source': admission.SOURCE, 'result': {'literal': 'independent'}}
        with patch.object(actual.json, 'loads', return_value=fixture), patch.object(actual.admission.W.__class__, 'read_bytes', return_value=b'fixture'):
            self.assertEqual('independent', actual.receipt('purefixture')['literal'])
        for key, value in [('actualExit', False), ('actualExit', 1), ('source', admission.previous.SOURCE), ('result', None)]:
            with patch.object(actual.json, 'loads', return_value={**fixture, key: value}), patch.object(actual.admission.W.__class__, 'read_bytes', return_value=b'fixture'):
                with self.assertRaises(ValueError):
                    actual.receipt('purefixture')

    def test_actual_guard_changes_only_one_release_authority(self):
        original = "before\n/opt/schubert-nk/releases/0.1.0-PG3976\nafter"
        current = actual.current_guard(original)
        self.assertEqual(original.replace('PG3976', 'PG4980'), current)
        for bad in (current, original + original, original.replace('PG3976', 'PG4860')):
            with self.assertRaisesRegex(ValueError, 'one exact prior'):
                actual.current_guard(bad)

    def test_composite_preserves_current_genuine_guard_and_entire_newday_oracle(self):
        original = root.payload(admission.live(), 'a' * 64)
        chain = {'before': {'history': 'old-source-is-data-only'}, 'after': {}, 'context': {}}
        raw = composite.compose(original, chain, 'b' * 64)
        joined = literal(raw, 'ORACLE')
        inner = {n.targets[0].id: ast.literal_eval(n.value) for n in ast.parse(joined).body
                 if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name)}
        self.assertEqual(chain, inner['CHAIN'])
        self.assertEqual(literal(original, 'ORACLE'), inner['ROOT_ORACLE'])
        self.assertEqual(literal(original, 'GUARD'), literal(raw, 'GUARD'))
        self.assertIn('def qualify_new_day', inner['ROOT_ORACLE'])
        self.assertIn(root.SLOT + '/before.private.json', joined)
        self.assertEqual(0, check(raw, '<whole exact current Browser chain>'))

    def test_parent18_is_data_only_and_composite_waits_original_owned_exit(self):
        raw = projection.payload('a' * 64)
        for marker in (admission.SOURCE, admission.BOM, composite.SLOT, "EXPECTED='" + 'a' * 64 + "'", 'len(fields)==18'):
            self.assertIn(marker, raw)
        self.assertNotIn('systemctl', raw)
        body = inspect.getsource(composite.previous.previous.main)
        self.assertLess(body.index("'start.safe.json'"), body.index('child.stdin.write'))
        self.assertIn('child.wait()', body)
        self.assertNotIn('timeout=', body)
        for p in (socks.__file__, ready.__file__, actual.__file__, composite.__file__, projection.__file__, __file__):
            self.assertEqual(0, checkPath(p))


if __name__ == '__main__':
    unittest.main()
