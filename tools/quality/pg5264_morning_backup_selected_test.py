import re
import unittest
import pg5264_morning_backup_selected as role


class MorningBackupScope(unittest.TestCase):
    def test_related18_cases_exact_four_suites(self):
        folder=role.selected.ROOT/'src/schubert-nk-batch/src/test/java'
        actual={}
        for name in role.RELATED:
            raw=(folder/(name.replace('.','/')+'.java')).read_text()
            cases=re.findall(r'@Test\s+void\s+([A-Za-z0-9_]+)\(',raw)
            self.assertEqual(len(cases),raw.count('@Test'))
            self.assertEqual(len(cases),len(set(cases)))
            actual[name.rpartition('.')[2]]=len(cases)
        self.assertEqual(actual,{'MorningBackupMetadataTest':4,'MorningBackupCatalogTest':1,
            'MorningBackupInputModeTest':3,'MorningBackupRetentionTest':10})
        self.assertEqual(sum(actual.values()),18)
        self.assertEqual(set(role.RELATED)-set(role.previous.extra_suites()),set(role.RELATED))
        self.assertEqual(len(role.extra_suites()),74)

    def test_three_semantic_six_bounded_debug_families(self):
        role.configure()
        self.assertEqual(len(role.selected.EXTRA_CHANGED),31)
        self.assertEqual(len(role.selected.EXTRA_DEBUG),66)


if __name__=='__main__':unittest.main()
