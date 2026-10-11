import ast
import inspect
import unittest
import pg1480_partial_profile_stage as stage
import pg1481_partial_original_profile as profile


class ReadonlyProfileTransportTest(unittest.TestCase):
    def test_exact_signature_done_receipts_missing_extra_or_foreign_rejected(self):
        expected=(b'PG1292 STAGE PINNED_SIGNATURE_VERIFIED\n'
                  b'PG1292 STAGE FULL_CANDIDATE_BOM_VERIFIED\n'
                  b'PG1481_DONE readonlyProfile=true allScopesReturnedNormally=true originalRetiredOrAuthorityIssued=false\n')
        self.assertTrue(profile.valid_receipt(expected))
        for changed in [None,expected.decode(),expected+b'\n',b'WARNING\n'+expected,
                        b''.join(expected.splitlines(keepends=True)[1:]),
                        b''.join(reversed(expected.splitlines(keepends=True))),
                        expected.replace(b'PG1292',b'PG1068'),expected.replace(b'Normal',b'Unknown')+b'!']:
            self.assertFalse(profile.valid_receipt(changed))

    def test_producer_consumer_share_exact_new_stage_slot(self):
        self.assertEqual('pg1480-partial-profile-stage-v1',stage.OUTNAME)
        self.assertEqual(stage.OUTNAME,profile.OUTNAME)
        self.assertIn('W / OUTNAME /',ast.unparse(ast.parse(inspect.getsource(profile.main))))
        self.assertIn("'OUT': previous.W / OUTNAME",ast.unparse(ast.parse(inspect.getsource(stage.main))))

    def test_once_profile_uses_compiled_pending_original_not_business_or_coverage(self):
        source=inspect.getsource(profile.main)
        for text in ['Pg1478PartialOriginalProfile','profileTimingQualificationPending','ownedRecoveryAccepted',"out.mkdir(mode=0o700)"]:
            self.assertIn(text,source)
        for text in ['StartUnit','StopUnit','systemctl','kill','--resume','jacoco']:self.assertNotIn(text,source)


if __name__=='__main__':unittest.main()
