"""Complete same-source qualification, distinct sessions and actual FFI oracle."""
import json
import unittest
from pyflakes.api import check
from pg1446_current_cold_stage import W
from pg3208_expiry_group_native_rejoin import build_payload
from pg3234_legacy_negative_native_join import build
from pg3238_legacy_negative_post import build as post


class CurrentNegativeQualification(unittest.TestCase):
    def seed(self):
        full = json.loads((W / 'pg3206-expiry-group-full-qualified-v1/manifest.safe.json').read_text())['result']
        old = json.loads((W / 'pg3056-boundary-group-full-qualified-v1/manifest.safe.json').read_text())['result']
        capsule = json.loads((W / 'pg3188-browser-native-qualified-v1/manifest.safe.json').read_text())
        return build_payload(full, old, capsule['manifestSha256'])

    def test_whole_28_stream_namespace_and_no_activation_inflation(self):
        raw = build(self.seed(), 'a' * 64, 'b' * 64)
        self.assertEqual(0, check(raw, '<whole a9 native27+negative1>'))
        for value in ["'qualifiedNativeActivations':3", "'qualifiedNativeStreams':28", "'qualifiedNegativeFixtureCohorts':1", "'negativeWholePassedCases':7", 'len(streams)==28', 'len(sessions)==28', "meta['sourceSnapshot']==full['sourceSnapshot']", "full['jarHashes'][m]", "v['actualPublicNativeReadConnects']>0", "v['privateManagerConnects']==0", "b'PG3236-LFACT-v5'", "whole['actualExit']==post['actualExit']==0"]:
            self.assertIn(value, raw)
        for bad in ['', 'A' * 64, 'a' * 63, None]:
            with self.assertRaises(ValueError): build(self.seed(), bad, 'b' * 64)
        with self.assertRaises(ValueError): build('not an exact27 qualified payload', 'a' * 64, 'b' * 64)

    def test_post_requires_actual_public_native_and_no_private_not_old_exec_seam(self):
        raw = 'HASHES={}\n' + post()
        self.assertEqual(0, check(raw, '<whole real default-FFI post>'))
        for value in ['observer-cohort-v5', 'cohort-native-v5.exec', 'PG3236-LFACT-v5', "v['actualPublicNativeReadConnects']>0", "v['privateManagerConnects']==0", "mutations==[]", "whole['syscallSha256']", "'syscall.private.log':syscalls"]:
            self.assertIn(value, raw)
        for invalid in ["v['actualSystemctlShowExecs']>0", 'cohort-v4', 'PG3230-LFACT']:
            self.assertNotIn(invalid, raw)


if __name__ == '__main__':
    unittest.main()
