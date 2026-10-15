import ast
import copy
import json
import subprocess
import unittest
from pyflakes.api import check
from pg1446_current_cold_stage import W
import pg3302_directional_group_full_six as whole
import pg3304_directional_group_full_qualified as independent
import pg3306_directional_group_native_rejoin as native


class DirectionalWholeIntegrationTest(unittest.TestCase):
    def test_actual_related85_one_new_method_four_test_files_no_main(self):
        whole.validate(subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip())

    def test_sha_literals_do_not_change_when_containing_old_count(self):
        head = '3701' + 'a' * 36; digest = '3701' + 'b' * 60
        raw = whole.server_source(head, digest)
        strings = [n.value for n in ast.walk(ast.parse(raw)) if isinstance(n, ast.Constant) and isinstance(n.value, str)]
        self.assertIn(head, strings); self.assertIn(digest, strings)
        self.assertEqual(0, check(raw, '<fixed whole3702>'))
        raw = independent.server()
        self.assertEqual(0, check(raw, '<independent whole3702>'))
        self.assertIn('(85, 17, 174)', raw)
        self.assertIn('(1299, 173, 568)', raw)

    def test_native28_keeps_original_negative3694_and_checks_whole3702(self):
        def read(slot):
            return json.loads((W / slot / 'manifest.safe.json').read_text())
        proposed = copy.deepcopy(read('pg3276-header-group-full-qualified-v1')['result']); proposed['tests'] = 3702
        raw = native.build(proposed, read('pg3206-expiry-group-full-qualified-v1')['result'], read('pg3056-boundary-group-full-qualified-v1')['result'], read('pg3188-browser-native-qualified-v1')['manifestSha256'], 'a' * 64, 'b' * 64)
        self.assertEqual(0, check(raw, '<sealed28 and new3702>'))
        for marker in ["'qualifiedFullTests':3702", "'qualifiedNativeStreams':28", 'PG3306-native-join-v1', "meta['sourceSnapshot']==ORIGINAL_FULL['sourceSnapshot']", "'source-full-PG3204/src'", 'require(images[0]==images[1])']:
            self.assertIn(marker, raw)
        actual = read('pg3278-header-group-native-qualified-v1')
        with self.assertRaises(ValueError):
            native.public_summary(actual)
        actual['result']['qualifiedFullTests'] = 3702
        self.assertEqual(3702, native.public_summary(actual)['tests'])
        actual['result']['qualifiedNativeStreams'] = 27
        with self.assertRaises(ValueError):
            native.public_summary(actual)


if __name__ == '__main__':
    unittest.main()
