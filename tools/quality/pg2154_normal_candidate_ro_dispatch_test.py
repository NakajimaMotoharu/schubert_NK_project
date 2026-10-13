import unittest
import pg2154_normal_candidate_ro_dispatch as p


class RoDispatch(unittest.TestCase):
    def test_actual_roles_and_whole_namespace(self):
        raw=p.source()
        for text in ['pg2153-frozen','pg2150-normal-unused-independent-post-v1','pg2144-current-normal-unused-tools-v1','Pg2152InputBoundaryTest','0.1.0-PG1846']:self.assertIn(text,raw)
        self.assertEqual(p.CLASS,'Pg2152CandidateRo')
        self.assertNotIn('0.1.0-PG1638',raw)
        self.assertNotIn('pg1868-frozen',raw)
        self.assertIn(p.TOOLS,p.STAGE)
        self.assertIn('pg2154-fixed-stage-v1',p.STAGE)
        from pyflakes.api import check
        context='\n'.join(n+'=None'for n in ['sys','subprocess','CANDIDATE','json','W','OLD','sources','hashlib','TARGET','os','Path','datetime','management_gate','P','tarfile','TOOLS','SSH','REMOTE','GUEST','OPTIONS','STAGE','CLASS','BEFORE'])+'\n'
        self.assertEqual(check(context+raw,'<actual RO entry namespace>'),0)


if __name__=='__main__':unittest.main()
