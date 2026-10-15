"""Current Header84/fixed two methods and SHA-preserving whole/native templates."""
import ast
import copy
import json
import subprocess
import unittest
from pyflakes.api import check
from pg1446_current_cold_stage import W
import pg3274_header_group_full_six as whole
import pg3276_header_group_full_qualified as independent
import pg3278_header_group_native_rejoin as native


class HeaderIntegrationTest(unittest.TestCase):
    def test_actual_header84_two_methods_unchanged_main(self):
        whole.validate(subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip())

    def test_head_and_archive_containing_old_digits_never_rewritten(self):
        head = '3699' + 'a' * 36; digest = '3699' + 'b' * 60
        raw = whole.server_source(head, digest)
        strings = [n.value for n in ast.walk(ast.parse(raw)) if isinstance(n, ast.Constant) and isinstance(n.value, str)]
        self.assertIn(head, strings); self.assertIn(digest, strings)
        self.assertNotIn('3701' + 'a' * 36, strings)
        self.assertEqual(0, check(raw, '<exact3701 fixed input server>'))
        normal = independent.server()
        self.assertEqual(0, check(normal, '<independent3701 complete>'))
        self.assertIn('(84, 17, 174)', normal)
        self.assertIn('(1299, 173, 568)', normal)

    def test_native28_retains_original_compile_provenance_and_dynamic_summary(self):
        def read(slot):
            return json.loads((W / slot / 'manifest.safe.json').read_text())
        proposed = copy.deepcopy(read('pg3260-statement-group-full-qualified-v1')['result']); proposed['tests'] = 3701
        raw = native.build(proposed, read('pg3206-expiry-group-full-qualified-v1')['result'], read('pg3056-boundary-group-full-qualified-v1')['result'], read('pg3188-browser-native-qualified-v1')['manifestSha256'], 'a' * 64, 'b' * 64)
        self.assertEqual(0, check(raw, '<same all Main/resources negative-provenance native28>'))
        for marker in ["'qualifiedFullTests':3701", "'qualifiedNativeStreams':28", 'PG3278-native-join-v1', "meta['sourceSnapshot']==ORIGINAL_FULL['sourceSnapshot']", "'source-full-PG3204/src'", 'require(images[0]==images[1])']:
            self.assertIn(marker, raw)
        actual = read('pg3262-statement-group-native-qualified-v1')
        with self.assertRaises(ValueError):
            native.public_summary(actual)
        actual['result']['qualifiedFullTests'] = 3701
        self.assertEqual(3701, native.public_summary(actual)['tests'])
        actual['result']['qualifiedNativeStreams'] = 27
        with self.assertRaises(ValueError):
            native.public_summary(actual)


if __name__ == '__main__':
    unittest.main()
