import unittest
import pg1423_retention_latest_counter as p

class Test(unittest.TestCase):
    def test_preserved_ready_and_latest_native_plus_new_retention(self):
        raw=p.source()
        for v in ('pg1415-readiness-latest-counter-v1','pg1414-batch-boundary-selected-v1/selected.exec','pg1422-batch-boundary-selected-v1','pg1423-retention-latest-counter-v1','len(data)==18','gainVs1415',"'freshSelectedTests':10",'MorningBackupRetention','sameSessionUnion0'):
            self.assertIn(v,raw)
        self.assertIn('bootstrap-0.exec\'not in data',raw)
        self.assertIn('require(len(closed)==1)',raw)
        self.assertNotIn('subprocess.run(args,stdout=log',raw)
        compile(raw,'<eighteen qualified graph>','exec')

if __name__=='__main__':unittest.main()
