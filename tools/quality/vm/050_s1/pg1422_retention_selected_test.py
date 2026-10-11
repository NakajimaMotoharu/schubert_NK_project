import unittest
import pg1422_retention_selected as p

class Test(unittest.TestCase):
    def test_actual_selection_and_module_environment(self):
        raw=p.source()
        self.assertIn('-Dtest=MorningBackupRetentionTest',raw)
        self.assertIn("'requiredSelectedTestCount':10",raw)
        self.assertEqual(5,len(p.CHANGED))
        self.assertEqual(10,sum(p.SUITES.values()))
        self.assertIn('fresh_xml(',raw)
        self.assertIn('dependencyNotReissued',raw)
        self.assertIn("'allBatchMainClassBytesEqual1279'",raw)
        compile(raw,'<complete retention command>','exec')

if __name__=='__main__':unittest.main()
