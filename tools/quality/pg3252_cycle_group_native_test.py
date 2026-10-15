"""No relabelled old harness provenance; all Main/resource bytes and CRC mandatory."""
import copy
import json
import unittest
from pyflakes.api import check
from pg1446_current_cold_stage import W
from pg3252_cycle_group_native_rejoin import build


class SealedNativeRejoin(unittest.TestCase):
    def inputs(self):
        def read(name): return json.loads((W / name / 'manifest.safe.json').read_text())
        original = read('pg3206-expiry-group-full-qualified-v1')['result']
        proposed = copy.deepcopy(original); proposed['tests'] = 3697
        return [proposed, original, read('pg3056-boundary-group-full-qualified-v1')['result'], read('pg3188-browser-native-qualified-v1')['manifestSha256'], 'a' * 64, 'b' * 64]

    def test_whole_namespace_members_not_jar_timestamp_or_old_test_count(self):
        raw = build(*self.inputs())
        self.assertEqual(0, check(raw, '<sealed native28 new3697>'))
        for item in ["meta['sourceSnapshot']==ORIGINAL_FULL['sourceSnapshot']", 'require(images[0]==images[1])', "'source-full-PG3204/src'", "ORIGINAL_FULL['jarHashes'][m]", "'qualifiedFullTests':3697", "'qualifiedNativeStreams':28", 'PG3252-native-join-v1', "native.read_bytes()==material['native.exec']"]:
            self.assertIn(item, raw)
        self.assertNotIn("with native.open('xb')", raw)
        self.assertNotIn("meta['sourceSnapshot']==full['sourceSnapshot']", raw)

    def test_either_foreign_source_is_refused_not_only_both_wrong(self):
        for index in [0, 1]:
            inputs = self.inputs(); inputs[index] = {**inputs[index], 'productionSource': 'foreign'}
            with self.assertRaises(ValueError): build(*inputs)


if __name__ == '__main__':
    unittest.main()
