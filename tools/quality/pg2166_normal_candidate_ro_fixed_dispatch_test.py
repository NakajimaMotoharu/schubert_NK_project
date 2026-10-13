import unittest
import pg2166_normal_candidate_ro_fixed_dispatch as p


class CompleteStage(unittest.TestCase):
    def test_actual_stage_and_main_role_matrix(self):
        self.assertIn('/opt/schubert-nk/releases/0.1.0-PG1846',p.STAGE)
        self.assertNotIn('0.1.0-PG1638',p.STAGE)
        self.assertIn('/home/ubuntu/pg2166-fixed-stage-v1/pg2164-normal-candidate-ro-tools-v1.tar',p.STAGE)
        self.assertIn(p.GUEST,p.STAGE)
        raw=p.source()
        self.assertIn('pg2165-frozen',raw)
        self.assertIn('pg2166-stage-v1.exit',raw)
        self.assertIn('Pg2164InputBoundaryTest',raw)
        self.assertEqual(p.CLASS,'Pg2164CandidateRo')
        self.assertNotIn('pg2153-frozen',raw)
        self.assertNotIn('0.1.0-PG1638',raw)


if __name__=='__main__':unittest.main()
