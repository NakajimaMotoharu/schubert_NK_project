"""Fixed whole3694 and27-session/member/fixture transport contracts; no VM work."""
import ast
import json
import unittest
from pyflakes.api import check
from pg1446_current_cold_stage import W
import pg3204_expiry_group_full_six as whole
import pg3206_expiry_group_full_qualified as qualified
import pg3208_expiry_group_native_rejoin as native


class FullExpiry(unittest.TestCase):
    def test_six_format_first_and_exact_scope_counts(self):
        raw = whole.server_source('a' * 40, 'b' * 64)
        compile(raw, '<whole3694>', 'exec')
        self.assertTrue('PG3204' in raw)
        self.assertTrue('3694' in raw)
        self.assertTrue(raw.index('format_result=subprocess.run(format_args') < raw.index('r=subprocess.run(args'))
        raw = qualified.server()
        for token in ['3694', "'batch':(1294,173,568)", 'PG3204']:
            self.assertTrue(token in raw, token)

    def test_native_rejects_old_whole_but_retains_old_capsule_qualification(self):
        old = json.loads((W / 'pg3056-boundary-group-full-qualified-v1/manifest.safe.json').read_bytes())['result']
        full = {**old, 'tests': 3694}
        raw = native.build_payload(full, old, 'a' * 64)
        ast.parse(raw)
        self.assertEqual(0, check(raw, '<whole new3694 native27>'))
        for token in ['PG3204-six-v1', 'PG3208', 'len(streams)==27', 'main_count==1643 and resource_count==79', "inputs[2]['qualifiedFull']==CAPSULE_FULL", "full['tests']==3694"]:
            self.assertTrue(token in raw, token)
        with self.assertRaises(ValueError):
            native.build_payload(old, old, 'a' * 64)


if __name__ == '__main__':
    unittest.main()
