import ast
import unittest
from unittest.mock import patch
import pg6922_db_fixture_selected as p
import test_support_profile as support


class DbFixtureDefinitionTest(unittest.TestCase):
    def test_actual_separate_red_and_combined_green_inventories(self):
        for mode, expected in (('red-bootstrap', (15, 8)), ('red-batch', (15, 8)), ('green', (21, 10))):
            cases, counts = p.inventory(mode)
            self.assertEqual(expected, (sum(counts.values()), len(counts)))
            self.assertEqual({'protocol', 'storage', 'bootstrap', 'api', 'web', 'batch'}, set(cases))

    def test_no_fabricated_main_target_percentage_and_full_verdict_retained(self):
        raw = support.runner(21, 10, {})
        tree = ast.parse(raw)
        value = [n.value for n in ast.walk(tree) if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'target100' for t in n.targets)]
        self.assertEqual(1, len(value))
        self.assertIsNone(value[0].value)
        for text in ('1669', 'exactInventory', 'sourceFixed', 'staticIssues', 'selectedQualified'):
            self.assertIn(text, raw)
        with self.assertRaises(ValueError):
            support.runner(21, 10, {'batch': ['fake']})

    def test_only_declared_fixture_and_new_test_paths_no_gate_change(self):
        paths = '\n'.join(sorted(p.FIXTURES | p.TESTS))
        with patch.object(p.subprocess, 'check_output', side_effect=[paths, b'']):
            p.guard('candidate')
        with patch.object(p.subprocess, 'check_output', return_value=paths + '\nMain.java'), self.assertRaises(ValueError):
            p.guard('candidate')
        with patch.object(p.subprocess, 'check_output', side_effect=[paths, b'gate change']), self.assertRaises(ValueError):
            p.guard('candidate')


if __name__ == '__main__':
    unittest.main()
