import unittest
from pyflakes.api import check
from pg2122_backup_metadata_selected import server

class Selection(unittest.TestCase):
    def test_actual_mandatory_four_suites_without_skip_or_namespace_collision(self):
        raw=server()
        self.assertEqual(0,check('HEAD="fixed"\nARCHIVE_SHA="fixed"\n'+raw,'<actual Backup metadata selection>'))
        self.assertIn('MorningBackupMetadataTest,BackupRetentionBoundaryTest,BackupArtifactVerifierTest,MorningBackupRetentionTest',raw)
        self.assertIn("'tests':4,'failures':0,'errors':0,'skipped':0",raw)
        self.assertNotIn('-DskipTests',raw)
        self.assertNotIn('PG2116',raw)
        self.assertNotIn('CaddyPublicMetadataTest',raw)

if __name__=='__main__':unittest.main()
