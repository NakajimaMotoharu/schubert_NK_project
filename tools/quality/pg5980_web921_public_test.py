import unittest
import pg5980_web921_public as t


class Web921OriginalQualificationTest(unittest.TestCase):
    def test_no_absent_zero_missed_or_wrong_target_count_can_pass(self):
        good = {str(i):{k:{'covered':1,'missed':0} for k in ('LINE','METHOD','CLASS','BRANCH')} for i in range(12)}
        self.assertTrue(t.four100(good))
        for bad in ({**good,'extra':good['0']}, {k:v for k,v in good.items() if k!='0'}, {**good,'0':{k:v for k,v in good['0'].items() if k!='BRANCH'}}, {**good,'0':{**good['0'],'BRANCH':{'covered':0,'missed':0}}}, {**good,'0':{**good['0'],'METHOD':{'covered':1,'missed':1}}}):
            self.assertFalse(t.four100(bad))
        self.assertEqual((149,921), (len(t.inventory()[1]),sum(t.inventory()[1].values())))


if __name__ == '__main__':
    unittest.main()
