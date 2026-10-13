import unittest
import pg2172_normal_publication_dispatch as p


class PublicationDispatch(unittest.TestCase):
    def test_entire_actual_stage_namespace_and_tuple(self):
        self.assertIn('/opt/schubert-nk/releases/0.1.0-PG1846',p.STAGE)
        self.assertNotIn('0.1.0-PG1638',p.STAGE)
        self.assertIn('/home/ubuntu/pg2172-fixed-stage-v1/pg2170-normal-publication-tools-v1.tar',p.STAGE)
        self.assertIn(p.GUEST,p.STAGE)
        raw=p.source()
        for text in ['pg2171-frozen','pg2172-stage-v1.exit','PG2170_INPUT_CLOSURE_READY','Pg2170TransitionTest','/opt/schubert-nk/releases/0.1.0-PG1846']:self.assertIn(text,raw)
        self.assertNotIn('0.1.0-PG1638',raw)
        self.assertNotIn('REGULAR_MORNING_UNIT_EXCHANGE',raw)
        self.assertEqual(p.CLASS,'Pg2170OrdinaryPublication')
        self.assertIn("'unitExchangeAndReload':False",raw)
        from pyflakes.api import check
        names=['sys','subprocess','CANDIDATE','json','W','OLD','sources','hashlib','TARGET','os','Path','datetime','management_gate','P','tarfile','TOOLS','SSH','REMOTE','GUEST','OPTIONS','STAGE','CLASS','BEFORE','BOM']
        self.assertEqual(check('\n'.join(n+'=None'for n in names)+'\n'+raw,'<actual normal publication namespace>'),0)


if __name__=='__main__':unittest.main()
