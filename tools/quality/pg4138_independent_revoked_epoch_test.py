import hashlib
import unittest
from pg4138_independent_revoked_epoch import former_issued


class RevokedEpochTest(unittest.TestCase):
    def test_independent_ss_literal_before_sha_after_no_production_expected(self):
        before=(b'NKEPOCH1\nstate=ISSUED\nboot_id=79a3260a-e16d-42bf-942a-b914ed144c28\n'
                b'epoch_id=11111111-2222-4333-8444-555555555555\nrun_id=dc0cb75f-1dbd-4b64-bb1c-b4d91e592c4f\n'
                b'cutoff_utc=2026-10-16T05:44:47.267413Z\nactivation_id=d9d58371-bf80-49f6-bad9-3d1e0916fb04\n'
                b'permit_sha256=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n')
        after=(b'NKEPOCH1\nstate=INVALID\nboot_id=79a3260a-e16d-42bf-942a-b914ed144c28\n'
               b'epoch_id=11111111-2222-4333-8444-555555555555\nrun_id=dc0cb75f-1dbd-4b64-bb1c-b4d91e592c4f\n'
               b'cutoff_utc=2026-10-16T05:44:47.267413Z\nactivation_id=d9d58371-bf80-49f6-bad9-3d1e0916fb04\npermit_sha256=-\n')
        self.assertEqual(before,former_issued(after,'a'*64))
        self.assertNotEqual(hashlib.sha256(before).digest(),hashlib.sha256(former_issued(after,'b'*64)).digest())
        for value in [None,b'',before,after+b'\n',after.replace(b'cutoff_utc=',b'cutoff='),after.replace(b'epoch_id=11111111-2222-4333-8444-555555555555',b'epoch_id=../../etc/shadow')]:
            with self.assertRaises(ValueError):former_issued(value,'a'*64)
        for digest in [None,'a'*63,'G'*64,'a'*65]:
            with self.assertRaises(ValueError):former_issued(after,digest)


if __name__=='__main__':unittest.main()
