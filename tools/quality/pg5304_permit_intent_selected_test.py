import re
import unittest
import pg5304_permit_intent_selected as role


class PermitIntentScope(unittest.TestCase):
    def test_related36_cases_new17_exact_existing_suites(self):
        folder=role.selected.ROOT/'src/schubert-nk-batch/src/test/java'
        actual={}
        for name in role.RELATED:
            raw=(folder/(name.replace('.','/')+'.java')).read_text()
            cases=re.findall(r'@Test\s+void\s+([A-Za-z0-9_]+)\(',raw)
            self.assertEqual(len(cases),raw.count('@Test'))
            self.assertEqual(len(cases),len(set(cases)))
            actual[name.rpartition('.')[2]]=len(cases)
        self.assertEqual(actual,{'BackupStartIntentFilesTest':6,'RootFailedStartPairRecoveryTest':11,
            'StartupPermitFilesTest':15,'MorningCompletedMainTest':4})
        self.assertEqual(sum(actual.values()),36)
        self.assertEqual(set(role.RELATED)-set(role.previous.extra_suites()),
            {'dev.codex.schubert.nk.batch.file.BackupStartIntentFilesTest','dev.codex.schubert.nk.batch.file.RootFailedStartPairRecoveryTest'})
        self.assertEqual(len(role.extra_suites()),95)

    def test_original_and_additional_inventory_remain_separate(self):
        role.configure()
        self.assertEqual(role.FILES,{'MorningPermitPublication'})
        self.assertEqual(role.EXTRA_FACTORY_FILES,{'BackupStartIntentFiles'})
        self.assertFalse(role.FILES&role.EXTRA_FACTORY_FILES)
        self.assertEqual(len(role.selected.EXTRA_CHANGED),50)
        self.assertEqual(len(role.selected.EXTRA_DEBUG),158)


if __name__=='__main__':unittest.main()
