import unittest
import pg5994_web24_public as t


class Actual24CountersTest(unittest.TestCase):
    def test_explicit24_classes_four_nonzero_covered_no_missed(self):
        good={str(i):{k:{'covered':1,'missed':0} for k in ('LINE','METHOD','CLASS','BRANCH')} for i in range(24)}
        self.assertTrue(t.four100(good))
        for bad in ({**good,'extra':good['0']},{k:v for k,v in good.items() if k!='0'},{**good,'0':{k:v for k,v in good['0'].items() if k!='BRANCH'}},{**good,'0':{**good['0'],'BRANCH':{'covered':0,'missed':0}}},{**good,'0':{**good['0'],'LINE':{'covered':1,'missed':1}}}):
            self.assertFalse(t.four100(bad))
        self.assertEqual((149,921),(len(t.inventory()[1]),sum(t.inventory()[1].values())))


if __name__ == '__main__':
    unittest.main()
