"""Exact source/input/native metadata gates, no runtime work or credit."""
import ast
import copy
import json
import subprocess
import unittest

from pyflakes.api import check

import pg3372_maintenance_group_integration as target


class MaintenanceIntegration(unittest.TestCase):
    def test_actual_related_and_beforeall_are_bound_to_current_inputs(self):
        head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=target.ROOT, text=True).strip()
        target.validate(head)

    def test_full_and_independent_count_template_preserves_digest_literals(self):
        head = '3704' + 'a' * 36; digest = '3704' + 'b' * 60
        raw = target.server_source(head, digest)
        literals = [n.value for n in ast.walk(ast.parse(raw)) if isinstance(n, ast.Constant) and isinstance(n.value, str)]
        self.assertIn(head, literals); self.assertIn(digest, literals)
        self.assertEqual(0, check(raw, '<whole3706>'))
        raw = target.independent_server()
        for value in ['(1302, 173, 568)', '(86, 17, 174)', '(163, 23, 74)']:
            self.assertIn(value, raw)

    def test_template_rebased_before_embedding_actual_data_and_original_history(self):
        def read(slot): return json.loads((target.W / slot / 'manifest.safe.json').read_bytes())
        full = copy.deepcopy(read('pg3352-oracle-boundary-full-qualified-v1')['result']); full['tests'] = 3706
        full['independentSentinelCounter'] = 3704
        raw = target.native_build(full, read('pg3206-expiry-group-full-qualified-v1')['result'],
            read('pg3056-boundary-group-full-qualified-v1')['result'],
            read('pg3188-browser-native-qualified-v1')['manifestSha256'], 'a' * 64, 'b' * 64)
        actual = next(ast.literal_eval(n.value) for n in ast.parse(raw).body if isinstance(n, ast.Assign)
                      and isinstance(n.targets[0], ast.Name) and n.targets[0].id == 'FULL')
        self.assertEqual(full, actual)
        self.assertEqual(3704, actual['independentSentinelCounter'])
        self.assertIn("'qualifiedFullTests': 3706", raw)
        self.assertIn('PG3376-native-join-v1', raw)
        self.assertIn("'source-full-PG3204/src'", raw)
        with self.assertRaises(ValueError):
            target.native_summary(read('pg3354-oracle-boundary-native-qualified-v1'))


if __name__ == '__main__':
    unittest.main()
