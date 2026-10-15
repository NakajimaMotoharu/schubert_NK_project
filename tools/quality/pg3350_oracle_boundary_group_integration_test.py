import ast
import copy
import json
import subprocess
import unittest
from pyflakes.api import check

import pg3350_oracle_boundary_group_integration as target


class OracleBoundaryIntegrationTest(unittest.TestCase):
    def test_actual_four_test_changes_two_added_methods_and_wrong_rejections(self):
        target.validate_tests(subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=target.ROOT, text=True).strip())

    def test_digest_preserved_and_independent_new_module_counts(self):
        head = '3702' + 'a' * 36; digest = '3702' + 'b' * 60
        raw = target.server_source(head, digest)
        literals = [n.value for n in ast.walk(ast.parse(raw)) if isinstance(n, ast.Constant) and isinstance(n.value, str)]
        self.assertIn(head, literals); self.assertIn(digest, literals)
        self.assertEqual(0, check(raw, '<whole3704>'))
        raw = target.independent_server()
        for expected in ['(86, 17, 174)', '(163, 23, 74)', '(1300, 173, 568)']:
            self.assertTrue(expected in raw, expected)

    def test_native28_all_members_and_historical_negative3694_preserved(self):
        def read(slot): return json.loads((target.W / slot / 'manifest.safe.json').read_text())
        full = copy.deepcopy(read('pg3332-stream-group-full-qualified-v1')['result']); full['tests'] = 3704
        full['independentSentinelCounter'] = 3702
        raw = target.native_build(full, read('pg3206-expiry-group-full-qualified-v1')['result'], read('pg3056-boundary-group-full-qualified-v1')['result'], read('pg3188-browser-native-qualified-v1')['manifestSha256'], 'a' * 64, 'b' * 64)
        actual_full = next(ast.literal_eval(n.value) for n in ast.parse(raw).body if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name) and n.targets[0].id == 'FULL')
        self.assertEqual(full, actual_full)
        self.assertEqual(3702, actual_full['independentSentinelCounter'])
        for expected in ["'qualifiedFullTests': 3704", "'qualifiedNativeStreams': 28", 'PG3354-native-join-v1', "meta['sourceSnapshot'] == ORIGINAL_FULL['sourceSnapshot']", "'source-full-PG3204/src'", 'require(images[0] == images[1])']:
            self.assertTrue(expected in raw, expected)
        old = read('pg3334-stream-group-native-qualified-v1')
        with self.assertRaises(ValueError): target.native_summary(old)
        old['result']['qualifiedFullTests'] = 3704
        self.assertEqual(3704, target.native_summary(old)['tests'])


if __name__ == '__main__':
    unittest.main()
