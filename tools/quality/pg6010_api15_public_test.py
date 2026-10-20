import unittest
import pg6010_api15_public as t


class Actual15CounterQualificationTest(unittest.TestCase):
    def test_exact_nonzero_four_counters_on_all15(self):
        good={str(i):{k:{'covered':1,'missed':0}for k in('LINE','METHOD','CLASS','BRANCH')}for i in range(15)}
        self.assertTrue(t.four100(good))
        for bad in ({**good,'extra':good['0']},{k:v for k,v in good.items()if k!='0'},{**good,'0':{k:v for k,v in good['0'].items()if k!='BRANCH'}},{**good,'0':{**good['0'],'BRANCH':{'covered':0,'missed':0}}},{**good,'0':{**good['0'],'METHOD':{'covered':1,'missed':1}}}):self.assertFalse(t.four100(bad))
        self.assertEqual((175,1021),(len(t.inventory()[1]),sum(t.inventory()[1].values())))


if __name__=='__main__':unittest.main()
