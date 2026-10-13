import unittest
from pg2418_question_unused_post import payload,production


class Post(unittest.TestCase):
    def test_independent_whole_retired_current_and_new_candidate_tuple(self):
        candidate={'actualExit':0,'candidateSource':production(),'signatureVerified':True,
                   'manifestSha256':'a'*64,'signatureSha256':'b'*64}
        raw=payload(candidate)
        for v in ['pg2416-question-unused-placement-v1','pg2410-retired-current-before-v1',
                  '0.1.0-PG2428',production(),'same_except_runtime','qualify_backup()',
                  'unusedCandidate187Verified','currentEpochApprovalUnchanged',
                  'genuineParentNormalWarningOriginal=true']:
            self.assertIn(v,raw)
        for v in ['pg2150-normal-unused-independent-post-v1','pidfd_send_signal',
                  'StartUnit(','StopUnit(','daemon-reload']:
            self.assertNotIn(v,raw)
        for field in candidate:
            wrong={**candidate,field:None}
            with self.assertRaises(ValueError):
                payload(wrong)


if __name__=='__main__':
    unittest.main()
