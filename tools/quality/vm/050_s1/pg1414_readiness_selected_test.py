"""Actual selected strict scope/known changed tests and preserved dependency source."""
import unittest
import pg1414_readiness_selected as p

class Test(unittest.TestCase):
    def test_whole_join(self):
        raw=p.source()
        self.assertEqual(4,len(p.CHANGED));self.assertEqual(11,sum(p.SUITES.values()))
        for s in ('-Dtest=MorningServiceReadinessTest,ArtemisRoleReadinessClientTest',"'requiredSelectedTestCount':11",'fresh_xml(p,suite','pg1408-batch-boundary-selected-v1/manifest.safe.json','dependencyNotReissued','allBatchMainClassBytesEqual1279'):
            self.assertIn(s,raw)
        self.assertNotIn('-Dtest=BatchRunRepositoryTest,BackupProfileTest',raw)
        compile(raw,'<actual readiness scope>','exec')

if __name__=='__main__':unittest.main()
