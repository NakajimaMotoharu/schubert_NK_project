"""Management definitions only; no production test or own fixture execution here."""
import unittest
import xml.etree.ElementTree as ET
from unittest.mock import patch
import pg6544_jdbc_transaction_selected as selected
import finite_selected_profile as profile
import pg6544_jdbc_original_red as red
import pg6548_jdbc_transaction_qualification as reader


class TransactionDefinitionTest(unittest.TestCase):
    def test_red_cannot_accept_timeout_or_wrong_assertion(self):
        method = 'tx329004CommitFatalWinsOverRollbackAndCloseFatals'
        message = ('expected: <[acquire, auto:false, handle, commit, rollback, close]> '
                   'but was: <[acquire, auto:false, handle, commit, close]>')
        red.validate_failure(method, ET.Element('failure', type='AssertionFailedError', message=message))
        for attrs in ({}, {'type': 'TimeoutException'}, {'type': 'AssertionFailedError', 'message': 'wrong'}):
            with self.assertRaises(ValueError):
                red.validate_failure(method, ET.Element('failure', attrs))

    def test_reader_fixed_two_main_and_exact_phases(self):
        with patch.object(reader, 'RUN') as run, patch.object(reader, 'guard_source') as guard, \
                patch.object(reader, 'qualify') as qualify:
            run.__truediv__.return_value.read_bytes.return_value = b'{"source":"fixture"}'
            reader.main()
        guard.assert_called_once_with('fixture', 'green')
        args, kwargs = qualify.call_args
        self.assertEqual((23, 9), args[3])
        self.assertEqual(selected.MAINS, args[4])
        self.assertEqual((0, 0, 0), kwargs['expected_phase_exits'])

    def test_exact_inventory_compile_before_selected(self):
        _, counts = selected.inventory()
        self.assertEqual((20, 8), (sum(counts.values()), len(counts)))
        raw = profile.runner(20, 8, selected.TARGETS)
        self.assertIn('exits==[0,0,0]', raw)
        self.assertLess(raw.index("['-DskipTests'"), raw.index("['-Dtest='"))
        _, green = selected.inventory('green')
        self.assertEqual((23, 9), (sum(green.values()), len(green)))

    def test_old_main_and_premature_green_guards(self):
        with patch.object(selected.subprocess, 'check_output', side_effect=[selected.TEST, b'']):
            selected.guard_source('fixture', 'red')
        with patch.object(selected.subprocess, 'check_output', return_value='unrelated Main'):
            with self.assertRaises(ValueError):
                selected.guard_source('fixture', 'red')
        changes = '\n'.join(sorted({selected.TEST, selected.GRAPH_TEST} | selected.MAINS))
        with patch.object(selected, 'RED_SOURCE', None), patch.object(selected.subprocess, 'check_output',
                side_effect=[changes, b'']):
            with self.assertRaisesRegex(ValueError, 'oracle bytes'):
                selected.guard_source('fixture', 'green')


if __name__ == '__main__':
    unittest.main()
