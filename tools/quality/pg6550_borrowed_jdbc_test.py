import unittest
import xml.etree.ElementTree as ET
from unittest.mock import patch
import finite_selected_profile as profile
import pg6550_borrowed_jdbc_selected as selected


class BorrowedJdbcDefinitionTest(unittest.TestCase):
    def test_inventory_compile_first(self):
        _, counts = selected.inventory()
        self.assertEqual((23, 9), (sum(counts.values()), len(counts)))
        raw = profile.runner(23, 9, selected.TARGETS)
        self.assertIn('exits==[0,0,0]', raw)
        self.assertLess(raw.index("['-DskipTests'"), raw.index("['-Dtest='"))

    def test_source_guards(self):
        with patch.object(selected.subprocess, 'check_output', side_effect=['\n'.join(selected.TESTS), b'']):
            selected.guard_source('fixture', 'red')
        with patch.object(selected.subprocess, 'check_output', return_value='unrelated Main'):
            with self.assertRaises(ValueError): selected.guard_source('fixture', 'red')
        changes = '\n'.join(selected.TESTS | selected.MAINS)
        with patch.object(selected, 'RED_SOURCE', None), patch.object(selected.subprocess, 'check_output', side_effect=[changes, b'']):
            with self.assertRaisesRegex(ValueError, 'oracle bytes'): selected.guard_source('fixture', 'green')

    def test_exact_red_assertions_only(self):
        for method, name in selected.METHODS.items():
            message = ('Unexpected exception type thrown, expected: <java.lang.AssertionError> '
                       'but was: <dev.codex.schubert.nk.api.persistence.'+name+'>')
            selected.validate_failure(method, ET.Element('failure', type='AssertionFailedError', message=message))
        for attrs in ({}, {'type': 'TimeoutException'}, {'type': 'AssertionFailedError', 'message': 'other'}):
            with self.assertRaises(ValueError):
                selected.validate_failure('borrowed329001UserSearch', ET.Element('failure', attrs))

    def test_green_reader_five_main_and_three_phases(self):
        with patch.object(selected, 'W') as w, patch.object(selected, 'guard_source') as guard, \
                patch.object(selected, 'qualify') as qualify:
            w.__truediv__.return_value.__truediv__.return_value.read_bytes.return_value = b'{"source":"fixture"}'
            selected.qualify_green()
        guard.assert_called_once_with('fixture', 'green')
        args, kwargs = qualify.call_args
        self.assertEqual((23, 9), args[3]); self.assertEqual(selected.MAINS, args[4])
        self.assertEqual((0, 0, 0), kwargs['expected_phase_exits'])


if __name__ == '__main__': unittest.main()
