import unittest
from pyflakes.api import check
from pg2440_question_normal_publication_sources import sources,BOM,BOOT,CURRENT,CURRENT_BOM,production


class Publication(unittest.TestCase):
    def test_complete_actual_normal_current_candidate_seven_finite_phases(self):
        values=sources();whole='\n'.join(values.values())
        self.assertIn('Pg2440OrdinaryPublication.java',values)
        for v in [BOM,BOOT,CURRENT,CURRENT_BOM,production(),'/opt/schubert-nk/releases/0.1.0-PG2428',
                  '/opt/schubert-nk/releases/0.1.0-PG2126','pg2424-question-candidate-host-ro-v1/after.private.json']:
            self.assertIn(v,whole)
        for v in ['REGULAR_MORNING_UNIT_EXCHANGE','NORMAL_DAEMON_RELOAD','3d69f5af',
                  'pg2167-normal-candidate-host-ro-v1','0.1.0-PG1846']:
            self.assertNotIn(v,whole)
        for name,body in values.items():
            if name.endswith('.py'):
                prefix="BUNDLE_HASH='pending-real-bundle'\n" if name=='pg2440_native_refs.py' else ''
                self.assertEqual(0,check(prefix+body,'<full publication '+name+'>'))


if __name__=='__main__':unittest.main()
