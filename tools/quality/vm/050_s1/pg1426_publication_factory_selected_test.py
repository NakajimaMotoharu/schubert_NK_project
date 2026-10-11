import unittest
import pg1426_publication_factory_selected as p

class Test(unittest.TestCase):
    def test_fixed_source_and_actual_environment(self):
        raw=p.source()
        self.assertEqual(6,len(p.CHANGED));self.assertEqual(7,sum(p.SUITES.values()))
        self.assertIn('-Dtest=MorningBackupRequestPublicationTest',raw)
        self.assertIn("'requiredSelectedTestCount':7",raw)
        self.assertIn('>=805306368',raw)
        self.assertIn('fresh_xml(',raw)
        self.assertIn('dependencyNotReissued',raw)
        compile(raw,'<full publication command>','exec')

if __name__=='__main__':unittest.main()
