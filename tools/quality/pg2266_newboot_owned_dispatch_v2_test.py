import unittest
from pyflakes.api import check
import pg2266_newboot_owned_dispatch_v2 as p


class CurrentWholeStage(unittest.TestCase):
    def test_exact_current_boot_outer_stage_and_new_once_slots(self):
        for v in ['b2d6f605-61cf-425f-8fbd-12d606f6ee66',p.prior.SOURCE,p.prior.BOM,p.GUEST,p.REMOTE,p.ARCHIVE]:self.assertIn(v,p.STAGE)
        self.assertNotIn('3d69f5af',p.STAGE);self.assertNotIn('pg2248-fixed-stage',p.STAGE)
        s=p.run_source();self.assertIn('pg2266-stage-v1.exit',s);self.assertNotIn('pg2248-',s)
        self.assertIn('pg2247-frozen-v1.safe.json',s)
        self.assertEqual(0,check('DIGEST="fixed"\nFILES={}\n'+p.STAGE,'<actual stage complete tuple>'))


if __name__=='__main__':unittest.main()
