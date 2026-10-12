"""Independent signed unused candidate vs unchanged-current fixed literals."""
import unittest
from pyflakes.api import check
import pg1685_unused_candidate_independent_post as p


class CandidatePostTest(unittest.TestCase):
    def test_complete_independent_signed_candidate_and_current(self):
        raw=p.payload()
        self.assertEqual(0,check(raw,'<new unused signed candidate full post>'))
        for text in ["len(c['artifacts'])==187", "c['versions']['schema']=='028'",'len(rows)==24',"lines[-2:]==[b'0',b'0']",'maxGapNanos',"['before.private.json','after.private.json']",'allNewScopesReturnedNormally=true', 'unusedCandidate187Verified']:
            self.assertIn(text,raw)
        for text in ['pidfd_send_signal','os.kill(','pg_terminate_backend','tar.extractall']:self.assertNotIn(text,raw)


if __name__=='__main__':unittest.main()
