import unittest
import pg2156_normal_candidate_ro_dispatch_fixed as p


class Stage(unittest.TestCase):
    def test_actual_stage_current_and_new_dispatch_slot(self):
        raw=p.STAGE.replace(p.TOOLS,p.prior.TOOLS)
        self.assertIn("pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG1846')",raw)
        self.assertNotIn('0.1.0-PG1638',raw)
        self.assertIn('/home/ubuntu/pg2156-fixed-stage-v1/pg2152-normal-candidate-ro-tools-v1-pg2156.tar',raw)
        self.assertIn('/var/lib/pgpt-s1-preservation/pg2152-normal-candidate-ro-tools-v1',raw)
        self.assertIn('pg2156-stage-v1.exit',p.source())
        self.assertNotIn('pg2154-stage-v1.exit',p.source())


if __name__=='__main__':unittest.main()
