import unittest
from pg2660_operation_unused_dispatch import STAGE, source
from pg2658_operation_candidate_sources import BOOT,TOOLS,ARCHIVE,CURRENT,SOURCE


class NewUnusedPreparation(unittest.TestCase):
    def test_whole_stage_exact_boot_roles_and_real_names(self):
        raw=source()
        for marker in [BOOT,TOOLS,TOOLS+'.tar']:self.assertIn(marker,STAGE)
        for marker in ['2f7ca23be804567a5d9a61636cf4c1d4ec96fcd0','pg2659-frozen','pg2656-current-a79-before-v1','program/characterization']:self.assertIn(marker,raw)
        self.assertIn('/opt/schubert-nk/releases/0.1.0-PG2512',raw)
        self.assertIn(ARCHIVE,raw)
        self.assertNotIn('pg2517-frozen',raw)
        self.assertNotIn('pg2518-current-strict-release-v1.tar',STAGE)


if __name__=='__main__':unittest.main()
