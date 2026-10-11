import unittest
import pg1427_publication_latest_counter as p

class Test(unittest.TestCase):
    def test_latest_native_preserved_three_prior_selected_and_partial_contract(self):
        raw=p.source()
        for v in ('pg1423-retention-latest-counter-v1','pg1422-batch-boundary-selected-v1/selected.exec','pg1414-batch-boundary-selected-v1/selected.exec','pg1426-batch-boundary-selected-v1','len(data)==19','observedPartialClasses','gainVs1423',"'freshSelectedTests':7",'MorningBackupRequestPublication',"'LINE':1,'METHOD':1,'CLASS':0,'BRANCH':0"):
            self.assertIn(v,raw)
        self.assertNotIn('newCounterClosedClasses',raw)
        self.assertIn('bootstrap-0.exec\'not in data',raw)
        compile(raw,'<complete partial graph>','exec')

if __name__=='__main__':unittest.main()
