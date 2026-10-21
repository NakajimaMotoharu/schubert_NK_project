"""Definition checks for independent purposeful-red handling, not actual counterexamples."""
import unittest
import xml.etree.ElementTree as ET
from unittest.mock import patch
import pg6534_jdbc_fatal_graph_selected as selected
import pg6536_jdbc_original_red as original
import finite_selected_profile as profile


class JdbcGraphDefinitionTest(unittest.TestCase):
    def test_three_exact_inventories_and_compile_first(self):
        for phase, expected in (('api-red', (16, 9)), ('web-red', (19, 10)), ('green', (23, 12))):
            _, counts = selected.inventory(phase)
            self.assertEqual(expected, (sum(counts.values()), len(counts)))
            raw = profile.runner(*expected, selected.PROFILES[phase][3])
            self.assertIn('exits==[0,0,0]', raw)
            self.assertLess(raw.index("['-DskipTests'"), raw.index("['-Dtest='"))

    def test_scope_guards_and_premature_green_reject(self):
        test_changes = '\n'.join(sorted(selected.TESTS))
        with patch.object(selected.subprocess, 'check_output', side_effect=[test_changes, b'']):
            selected.guard_source('fixed-fixture', 'api-red')
        with patch.object(selected.subprocess, 'check_output', return_value='unexpected Main'):
            with self.assertRaises(ValueError):
                selected.guard_source('fixed-fixture', 'api-red')
        changes = '\n'.join(sorted(selected.TESTS | selected.MAINS))
        with patch.object(selected, 'RED_SOURCE', None), patch.object(selected.subprocess, 'check_output', side_effect=[changes, b'']):
            with self.assertRaisesRegex(ValueError, 'Test bytes fixed'):
                selected.guard_source('fixed-fixture', 'green')

    def test_only_exact_fatal_assertion_is_counterexample(self):
        accepted = ET.Element('failure', type='org.opentest4j.AssertionFailedError',
             message='Expected java.lang.AssertionError to be thrown, but nothing was thrown.')
        original.require_missing_fatal_assertion(accepted)
        for attrs in ({}, {'type':'TimeoutException'}, {'type':'AssertionFailedError','message':'unexpected equal failure'}):
            with self.assertRaises(ValueError):
                original.require_missing_fatal_assertion(ET.Element('failure', attrs))


if __name__ == '__main__':
    unittest.main()
