import unittest
from pyflakes.api import check
import pg2248_newboot_owned_dispatch as p


class CurrentOwnedEntry(unittest.TestCase):
    def test_entire_newslot_current_stage_and_once_action(self):
        for text in ['0.1.0-PG2126',p.SOURCE,p.BOM,p.GUEST,p.ARCHIVE]:self.assertIn(text,p.STAGE)
        self.assertNotIn('pg2188',p.STAGE)
        self.assertNotIn('pg2190',p.STAGE)
        self.assertIn('b2d6f605-61cf-425f-8fbd-12d606f6ee66',p.STAGE)
        self.assertNotIn('3d69f5af',p.STAGE)
        raw=p.run_source()
        for text in ['pg2247','pg2248','pg2249','pg2250-newboot-pre-stop-full-v1','Pg2246','PG2126']:
            self.assertIn(text,raw)
        for text in ['pg2189','pg2190','Pg2188']:self.assertNotIn(text,raw)
        ns={**p.prior.prior.runner.__dict__,'GUEST':p.GUEST,'REMOTE':p.REMOTE,'ARCHIVE':p.ARCHIVE,'STAGE':p.STAGE,'PARENT_PREQUAL':p.PARENT_PREQUAL,'sources':p.sources,'context':p.context,'SOURCE':p.SOURCE,'TOOLS':p.TOOLS,'POST_SLOT':p.POST_SLOT,'post_payload':p.post_payload}
        exec(compile(raw,'<full actual current entry exports>','exec'),ns)
        with self.assertRaises(ValueError):ns['run_action']('start')
        self.assertEqual(0,check('DIGEST="x"\nFILES={}\n'+p.STAGE,'<actual immutable current stage>'))
        self.assertEqual(0,check('GUEST="x"\nHASHES={}\n'+p.PARENT_PREQUAL,'<actual deployed parent prequal>'))


if __name__=='__main__':unittest.main()
