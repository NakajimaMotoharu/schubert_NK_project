import ast
import inspect
import unittest
import pg1480_partial_profile_stage as stage
import pg1481_partial_original_profile as profile


class ReadonlyProfileTransportTest(unittest.TestCase):
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
