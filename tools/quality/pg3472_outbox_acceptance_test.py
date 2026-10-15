import ast
import unittest
from unittest.mock import patch
from pyflakes.api import check
import pg3470_outbox_admission_before as before
import pg3472_outbox_acceptance as current


class CurrentIndependentPhases(unittest.TestCase):
    def test_actual_day16_immutable_oracle_not_old_same_day_factory(self):
        raw = current.rows_payload()
        ast.parse(raw)
        self.assertEqual(0, check(raw, '<actual day16 independent full24>'))
        for marker in ["r['business_date']=='2026-10-16'", current.ONCE, current.ROWS,
                       'pg3470-outbox-admission-before-v1/oracle.private.json',
                       '095a73c7a6d7511accbdf7eb169aa3e70050e8c4cce4dfe144857c0cbd9e7ae9',
                       '4f9084e09129be6e80bc0bca51c469cf5a5a6b616ece463e660a24de45806ebb']:
            self.assertTrue(marker in raw, marker)
        self.assertNotIn('ALREADY_SUCCESSFUL', raw)

    def test_actual_admission_image_and_old_native_preservation_only(self):
        ast.parse(before.BODY)
        for marker in [current.ONCE, '745b9c300446e11bd4230df34617f0bbf8ed738c8ea457ed2d107cd515aa717e',
                       "v['native']==expected['native']", "'execEntries':22"]:
            self.assertTrue(marker in before.BODY, marker)
        self.assertNotIn('==41', before.BODY)
        self.assertEqual(0, check(before.payload(), '<actual full before selector namespace>'))

    def test_terminal_and_seal_bound_to_same_source_and_generation(self):
        binding = {'run': '11111111-1111-4111-8111-111111111111',
                   'cutoff': '2026-10-15T16:49:02.160964Z',
                   'activation': '22222222-2222-4222-8222-222222222222',
                   'boot': current.BOOT.replace('-', ''), 'invocation': 'a' * 32,
                   'job': '92576', 'start': 82190409233, 'rootPid': 321930}
        with patch.object(current, 'before', return_value='a' * 64):
            values = [current.terminal_payload(binding), current.seal_payload(binding)]
        for raw in values:
            ast.parse(raw)
            self.assertEqual(0, check(raw, '<whole independent exact candidate phase>'))
            self.assertTrue(current.SOURCE in raw)
            self.assertNotIn('PG2654', raw)
            self.assertNotIn('b2d6f605', raw)
        self.assertTrue(current.ONCE in values[-1])
        self.assertTrue(current.SEAL in values[-1])
        node = next(n for n in ast.parse(values[-1]).body if isinstance(n, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id == 'ORACLE' for t in n.targets))
        oracle = ast.literal_eval(node.value)
        self.assertEqual(0, check(oracle, '<actual whole-seal independent day16 oracle>'))
        for marker in ["r['business_date']=='2026-10-16'", "row['business_date']=='2026-10-16'",
                       binding['cutoff'], binding['run']]:
            self.assertTrue(marker in oracle, marker)
        self.assertNotIn('ALREADY_SUCCESSFUL', oracle)
        with self.assertRaises(ValueError):
            current.entry('start')


if __name__ == '__main__':
    unittest.main()
