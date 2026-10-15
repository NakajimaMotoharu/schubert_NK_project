"""Exact selected63 bytes, whole3699 source and preserved old runtime provenance."""
import copy
import json
import subprocess
import unittest
from pyflakes.api import check
from pg1446_current_cold_stage import W
from pg3258_statement_group_full_six import validate, server_source
from pg3260_statement_group_full_qualified import server
from pg3262_statement_group_native_rejoin import build


class StatementIntegration(unittest.TestCase):
    def test_actual_selected63_and_two_methods(self):
        validate(subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip())
        raw = server_source('0' * 40, '1' * 64)
        self.assertEqual(0, check(raw, '<whole3699>'))
        self.assertIn('PG3258', raw); self.assertIn('3699', raw)
        self.assertIn("'batch':(1299,173,568)", server())

    def test_native28_all_members_not_relabelled_old_harness(self):
        def read(name): return json.loads((W / name / 'manifest.safe.json').read_text())
        original = read('pg3206-expiry-group-full-qualified-v1')['result']
        proposed = copy.deepcopy(read('pg3250-cycle-group-full-qualified-v1')['result']); proposed['tests'] = 3699
        raw = build(proposed, original, read('pg3056-boundary-group-full-qualified-v1')['result'], read('pg3188-browser-native-qualified-v1')['manifestSha256'], 'a' * 64, 'b' * 64)
        self.assertEqual(0, check(raw, '<same1643/79 native28 new3699>'))
        for item in ["'qualifiedFullTests':3699", "'qualifiedNativeStreams':28", 'PG3262-native-join-v1', "meta['sourceSnapshot']==ORIGINAL_FULL['sourceSnapshot']", "'source-full-PG3204/src'", 'require(images[0]==images[1])']:
            self.assertIn(item, raw)
        self.assertNotIn("with native.open('xb')", raw)


if __name__ == '__main__':
    unittest.main()
