import unittest
from pg4178_pool_bounds import counts_valid


class PoolBoundsTest(unittest.TestCase):
    def test_all_independent_normal_and_stopped_bounds_owned_separate(self):
        for api in range(2,9):
            for web in [1,2]:
                for owned in [0,1]:self.assertTrue(counts_valid({'schubert_app':api,'schubert_web_session':web},set(),owned,api+web+owned))
        for api,web,done in [(0,1,{'schubert-nk-api.service'}),(2,0,{'schubert-nk-web.service'}),(0,0,{'schubert-nk-api.service','schubert-nk-web.service'})]:
            for owned in [0,1]:self.assertTrue(counts_valid({'schubert_app':api,'schubert_web_session':web},done,owned,api+web+owned))

    def test_under_over_extra_null_bool_wrong_total_or_stopped_residue(self):
        for api,web in [(1,1),(9,1),(2,0),(2,3)]:self.assertFalse(counts_valid({'schubert_app':api,'schubert_web_session':web},set(),0,api+web))
        self.assertFalse(counts_valid({'schubert_app':2,'schubert_web_session':1},{'schubert-nk-web.service'},0,3))
        self.assertFalse(counts_valid({'schubert_app':2,'schubert_web_session':1},set(),1,3))
        for counts in [None,{}, {'unknown':1}, {'schubert_app':True,'schubert_web_session':1}, {'schubert_app':-1,'schubert_web_session':1}]:
            with self.assertRaises(ValueError):counts_valid(counts,set(),0,3)
        for owned in [None,True,2]:
            with self.assertRaises(ValueError):counts_valid({'schubert_app':2,'schubert_web_session':1},set(),owned,3)
        with self.assertRaises(ValueError):counts_valid({'schubert_app':2,'schubert_web_session':1},{'foreign.service'},0,3)


if __name__=='__main__':unittest.main()
