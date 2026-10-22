import unittest

import pg6990_recovery_public_scan as p


class RecoveryPublicScopeTest(unittest.TestCase):
    def test_exact_two_common_paths_not_private_native_or_arbitrary_material(self):
        self.assertTrue(all(p.allowed(v) for v in p.COMMON))
        for path in ('/run/anything','/home/mini/work/private/data','private/raw.log',
                     'evidence/01_PT/private/data','documents/data.private.log',
                     'program/characterization/tests/java/NativeUnreviewed.java','unrelated/data'):
            self.assertFalse(p.allowed(path))

    def test_empty_safe_and_known_format_detected_without_saving_match(self):
        self.assertEqual([],p.scan.inspect_bytes(b'public declaration only'))
        self.assertEqual('AWS_ACCESS_KEY_ID',p.scan.inspect_bytes(b'AK' + b'IA' + b'0'*16)[0]['rule'])


if __name__=='__main__':unittest.main()
