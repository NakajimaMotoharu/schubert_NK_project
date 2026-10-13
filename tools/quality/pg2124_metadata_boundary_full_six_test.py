import unittest
from pyflakes.api import check
from pg2124_metadata_boundary_full_six import server_source,production
from pg2125_metadata_boundary_full_qualification import server

class WholeSourceContract(unittest.TestCase):
    def test_whole_generated_counts_and_source_are_fixed(self):
        raw=server_source('1'*40,'2'*64)
        self.assertEqual(0,check(raw,'<actual whole server>'))
        self.assertIn('tests==3631',raw)
        self.assertIn('suites==540',raw)
        self.assertIn('classes==1643',raw)
        self.assertIn(production(),raw)
        self.assertNotIn('PG1844',raw)
        self.assertNotIn('0fd734195b4d5338f6b7e860e087cce561d49562',raw)

    def test_independent_qualifier_has_three_changed_classes_and_no_added_main(self):
        raw=server()
        self.assertEqual(0,check(raw,'<actual whole qualifier>'))
        self.assertIn("'batch':(1234,172,568)",raw)
        self.assertIn("require(added==[])",raw)
        self.assertIn('CaddyPublicConfiguration.class',raw)
        self.assertIn('RootStartupContext.class',raw)
        self.assertIn('MorningBackupArtifacts.class',raw)
        self.assertIn('RootStartupContext$NativeIo.class',raw)
        self.assertIn("debug['verify'](a,bnew,1)",raw)
        self.assertIn("B/'runs/PG1844-six-v1/manifest.safe.json'",raw)

if __name__=='__main__':unittest.main()
