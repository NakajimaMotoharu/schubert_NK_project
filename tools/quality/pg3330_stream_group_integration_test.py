import ast
import json
import subprocess
import unittest

from pyflakes.api import check

import pg3330_stream_group_integration as target


class StreamIntegrationTest(unittest.TestCase):
    def test_actual_related_same_one_test_change_and_before_failure(self):
        target.validate(subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=target.ROOT, text=True).strip())

    def test_late_digest_binding_and_all_module_counts_kept(self):
        head = '3702' + 'a' * 36; digest = '3702' + 'b' * 60
        raw = target.server_source(head, digest)
        strings = [n.value for n in ast.walk(ast.parse(raw)) if isinstance(n, ast.Constant) and isinstance(n.value, str)]
        self.assertIn(head, strings); self.assertIn(digest, strings)
        self.assertEqual(0, check(raw, '<whole stream3702>'))
        self.assertIn('PG3330', raw); self.assertNotIn('PG3302', raw)
        raw = target.independent_server()
        for literal in ['(85, 17, 174)', '(163, 23, 74)', '(1299, 173, 568)']:
            self.assertIn(literal, raw)

    def test_native28_keeps_original_provenance_and_new_whole(self):
        def read(slot):
            return json.loads((target.W / slot / 'manifest.safe.json').read_text())
        raw = target.native_build(read('pg3304-directional-group-full-qualified-v1')['result'], read('pg3206-expiry-group-full-qualified-v1')['result'], read('pg3056-boundary-group-full-qualified-v1')['result'], read('pg3188-browser-native-qualified-v1')['manifestSha256'], 'a' * 64, 'b' * 64)
        for marker in ["'qualifiedFullTests': 3702", "'qualifiedNativeStreams': 28", 'PG3334-native-join-v1', "meta['sourceSnapshot'] == ORIGINAL_FULL['sourceSnapshot']", "'source-full-PG3204/src'", 'require(images[0] == images[1])']:
            self.assertTrue(marker in raw, marker)
        self.assertNotIn('PG3306-native-join-v1', raw)


if __name__ == '__main__':
    unittest.main()
