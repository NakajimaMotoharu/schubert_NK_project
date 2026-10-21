"""Runner definition checks, not Production PT or coverage."""
import unittest
from unittest.mock import patch
import pg6512_finite_policy_factories as selected
import pg6514_finite_policy_qualification as reader


class FinitePolicyDefinitionTest(unittest.TestCase):
    def test_exact_inventory_and_three_phases(self):
        cases, counts = selected.inventory()
        self.assertEqual((20, 8), (sum(counts.values()), len(counts)))
        self.assertIn('api.file.ServiceResourceRetentionTest', cases['bootstrap'])
        raw = selected.selected_runner()
        self.assertIn("['-DskipTests','test-compile']", raw)
        self.assertIn('exits==[0,0,0]', raw)
        self.assertLess(raw.index("['spotless:check']"), raw.index("['-DskipTests'"))
        self.assertLess(raw.index("['-DskipTests'"), raw.index("['-Dtest='"))
        self.assertNotIn('done=done and target100', raw)
        compile(raw, '<finite policy checked>', 'exec')

    def test_guard_rejects_extra_main_and_changed_gate(self):
        selected.guard_source('a03b6153469f3478ed3b40d2c82e3f89c4d221ab')
        with patch.object(selected.subprocess, 'check_output', return_value='extra Main'):
            with self.assertRaises(ValueError):
                selected.guard_source('HEAD')

    def test_whole_source_and_terminal_cannot_be_substituted(self):
        import json
        original = json.loads(selected.Q.read_bytes())
        for key, wrong in (('productionSource', 'other'), ('returnedOriginalTerminalExact', False),
                           ('FESFlakyNotRun', 1)):
            changed = dict(original, **{key: wrong})
            with patch.object(selected.json, 'loads', return_value=changed):
                with self.assertRaises(ValueError):
                    selected.guard_source('HEAD')
        with patch.object(selected.subprocess, 'check_output', side_effect=[selected.TEST+'\n', b'gate']):
            with self.assertRaises(ValueError):
                selected.guard_source('HEAD')

    def test_reader_same_original_and_no_main_change(self):
        with patch.object(reader, 'guard_source') as guard, patch.object(reader, 'qualify') as qualify:
            with patch.object(reader, 'RUN') as run:
                run.__truediv__.return_value.read_bytes.return_value = b'{"source":"fixed-source"}'
                reader.main()
        guard.assert_called_once_with('fixed-source')
        args, kwargs = qualify.call_args
        self.assertEqual((20, 8), args[3])
        self.assertEqual(set(), args[4])
        self.assertEqual((0, 0, 0), kwargs['expected_phase_exits'])


if __name__ == '__main__':
    unittest.main()
