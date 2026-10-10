import ast
import unittest
from pg1302_current_candidate_ro_dispatch import source,STAGE,GUEST


class CandidateRoDispatchTest(unittest.TestCase):
    def test_complete_real_namespace_and_no_candidate_archive(self):
        ast.parse(source());ast.parse(STAGE)
        self.assertIn("(['stage'],['prepare-ro'])",source())
        self.assertIn('Pg1300CandidateRo prepare-ro',source())
        self.assertIn('Pg1300OriginalTupleTest',source())
        self.assertNotIn('UnusedStage place',source())
        self.assertNotIn('pg1295-release-v1.tar',STAGE)
        self.assertIn('pg1302-fixed-stage-v1/pg1300-native-tools-v1.tar',STAGE)
        self.assertEqual(GUEST,'/var/lib/pgpt-s1-preservation/pg1300-native-tools-v1')


if __name__=='__main__':unittest.main()
