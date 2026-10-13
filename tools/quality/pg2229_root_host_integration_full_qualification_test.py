import unittest
from pg2229_root_host_integration_full_qualification import server
from pyflakes.api import check


class CurrentFullQualification(unittest.TestCase):
    def test_exact_batch_plus_two_and_all_main_physical_delta(self):
        s=server()
        self.assertEqual(0,check(s,'<whole current provenance>'))
        for v in ['PG2228','3633',"'batch':(1236,172,568)",'540','1643',
          'RootStartupContext$NativeIo.class','debugLineQualification','semanticChangedClasses','debugOnlyChangedClasses']:
            self.assertIn(v,s)
        self.assertNotIn('source-full-PG2124',s)
        self.assertNotIn('==3631',s)


if __name__=='__main__':unittest.main()
