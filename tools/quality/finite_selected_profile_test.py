"""Shared finite-profile constraints; no PT execution or evidence generation here."""
import unittest
from unittest.mock import patch
import finite_selected_profile as profile
import pg6520_maintenance_owner_selected as selected
import pg6522_maintenance_owner_qualification as reader


class FiniteProfileTest(unittest.TestCase):
    def test_inventory_phase_order_and_no_coverage_promotion(self):
        _, counts = selected.inventory()
        self.assertEqual((15, 8), (sum(counts.values()), len(counts)))
        raw = profile.runner(15, 8, {'bootstrap': ['api/file/InspectorCredentialLoader']})
        self.assertLess(raw.index("['spotless:check']"), raw.index("['-DskipTests'"))
        self.assertLess(raw.index("['-DskipTests'"), raw.index("['-Dtest='"))
        self.assertIn('exits==[0,0,0]', raw)
        self.assertNotIn('done=done and target100', raw)
        compile(raw, '<checked finite profile>', 'exec')

    def test_incomplete_or_unknown_targets_reject_before_execution(self):
        for total, suites, targets in ((11, 8, {'bootstrap': ['x']}), (15, 6, {}),
                                       (15, 8, {'unknown': ['x']}), (15, 8, {'bootstrap': []})):
            with self.assertRaises(ValueError):
                profile.runner(total, suites, targets)
        with self.assertRaises(ValueError):
            profile.inventory({}, (15, 8))

    def test_guard_keeps_main_and_gate_constraints(self):
        with patch.object(selected.subprocess, 'check_output', side_effect=[selected.TEST+'\n', b'']):
            selected.guard_source('explicit-fixture')
        for responses in (['wrong Main'], [selected.TEST+'\n', b'changed gate']):
            with patch.object(selected.subprocess, 'check_output', side_effect=responses):
                with self.assertRaises(ValueError):
                    selected.guard_source('explicit-fixture')

    def test_reader_uses_original_and_empty_main_delta(self):
        with patch.object(reader, 'W') as work, patch.object(reader, 'guard_source') as guard, \
                patch.object(reader, 'qualify') as qualify:
            work.__truediv__.return_value.__truediv__.return_value.read_bytes.return_value = b'{"source":"original"}'
            reader.main()
        guard.assert_called_once_with('original')
        args, kwargs = qualify.call_args
        self.assertEqual((15, 8), args[3])
        self.assertEqual(set(), args[4])
        self.assertEqual((0, 0, 0), kwargs['expected_phase_exits'])


if __name__ == '__main__':
    unittest.main()
