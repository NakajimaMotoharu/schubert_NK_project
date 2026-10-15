"""Whole native27 namespace and exact cardinality/session/member proof boundaries."""
import unittest
import json
from pg1446_current_cold_stage import W
import pg3058_boundary_group_native_rejoin as historical
import pg3190_browser_three_activation_join as current


class ThreeActivation(unittest.TestCase):
    def test_all_three_capsules_unique_sessions_and_inspector_dominance(self):
        full = json.loads((W / 'pg3056-boundary-group-full-qualified-v1/manifest.safe.json').read_bytes())['result']
        seed = historical.build_payload(full)
        raw = current.expand(seed, 'a' * 64)
        for value in ["B/'runs/PG3188-native-v1'", 'len(streams)==27', 'len(sessions)==27',
                      "for s in sessions})==27", "'qualifiedNativeActivations':3",
                      "'qualifiedNativeStreams':27", "inputs[2]['qualifiedFull']==FULL",
                      'main_count==1643 and resource_count==79', 'NativePointDominance',
                      'for root,v,digest in zip(roots,inputs,MANIFESTS,strict=True)',
                      'for n,h in v[\'files\'].items():require(sha(root/n)==h)']:
            self.assertTrue(value in raw, value)
        for invalid in [None, '', 'a' * 63, 'A' * 64, 'g' * 64]:
            with self.assertRaises(ValueError):
                current.expand(seed, invalid)
        with self.assertRaises(ValueError):
            current.expand('roots=[]', 'a' * 64)


if __name__ == '__main__':
    unittest.main()
