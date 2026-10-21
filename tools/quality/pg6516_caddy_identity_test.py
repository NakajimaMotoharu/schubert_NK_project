"""Definition checks only, no Production Test execution by this module."""
import json
import unittest
from unittest.mock import patch
import pg6516_caddy_identity_literals as selected
import pg6518_caddy_identity_qualification as reader


class LiteralDefinitionTest(unittest.TestCase):
    def test_inventory_three_phases(self):
        cases, counts = selected.inventory()
        self.assertEqual((15, 8), (sum(counts.values()), len(counts)))
        self.assertIn('bootstrap.FixedCaddyIdentityTest', cases['bootstrap'])
        raw = selected.selected_runner()
        self.assertIn('exits==[0,0,0]', raw)
        self.assertLess(raw.index("['-DskipTests'"), raw.index("['-Dtest='"))
        compile(raw, '<literal fifteen>', 'exec')

    def test_reject_changed_main_gate_or_other_source(self):
        with patch.object(selected.subprocess, 'check_output', side_effect=[selected.TEST+'\n', b'']):
            selected.guard_source('HEAD')
        for responses in (['extra Main'], [selected.TEST+'\n', b'gate']):
            with patch.object(selected.subprocess, 'check_output', side_effect=responses):
                with self.assertRaises(ValueError):
                    selected.guard_source('HEAD')
        q = json.loads(selected.Q.read_bytes())
        for changed in (dict(q, source='other'), dict(q, changedPhysical=['Main']),
                        dict(q, actualExit=1)):
            with patch.object(selected.json, 'loads', return_value=changed):
                with self.assertRaises(ValueError):
                    selected.guard_source('HEAD')

    def test_reader_binds_original_and_empty_main_delta(self):
        with patch.object(reader, 'RUN') as run, patch.object(reader, 'guard_source') as guard, \
                patch.object(reader, 'qualify') as qualify:
            run.__truediv__.return_value.read_bytes.return_value = b'{"source":"fixed"}'
            reader.main()
        guard.assert_called_once_with('fixed')
        args, kwargs = qualify.call_args
        self.assertEqual((15, 8), args[3])
        self.assertEqual(set(), args[4])
        self.assertEqual((0, 0, 0), kwargs['expected_phase_exits'])


if __name__ == '__main__':
    unittest.main()
