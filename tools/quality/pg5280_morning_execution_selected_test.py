import re
import unittest
import pg5280_morning_execution_selected as role


class MorningExecutionScope(unittest.TestCase):
    def test_related85_cases_nine_new_suites70_cases(self):
        folder=role.selected.ROOT/'src/schubert-nk-batch/src/test/java'
        actual={}
        for name in role.RELATED:
            raw=(folder/(name.replace('.','/')+'.java')).read_text()
            cases=re.findall(r'@Test\s+void\s+([A-Za-z0-9_]+)\(',raw)
            self.assertEqual(len(cases),raw.count('@Test'))
            self.assertEqual(len(cases),len(set(cases)))
            actual[name.rpartition('.')[2]]=len(cases)
        self.assertEqual(actual,{'MorningBackupStageTest':9,'MorningCleanupCompletionTest':1,
            'MorningCompletedMainTest':4,'MorningCompletionEvidenceTest':11,'MorningControlScopeTest':19,
            'MorningCurrentInvalidationTest':6,'MorningPrestartEvidenceTest':5,'MorningResumeAdmissionTest':11,
            'MorningStartupRootsTest':4,'StartupPermitFilesTest':15})
        self.assertEqual(sum(actual.values()),85)
        self.assertEqual(set(role.RELATED)&set(role.previous.extra_suites()),{'dev.codex.schubert.nk.batch.file.StartupPermitFilesTest'})
        self.assertEqual(len(role.extra_suites()),89)

    def test_nested_completion_is_explicit_semantic_not_debug(self):
        role.configure()
        self.assertIn('MorningBrokerExecution$Completion',role.OUTERS)
        self.assertNotIn('MorningBrokerExecution$Completion',role.DEBUG)
        self.assertEqual(len(role.selected.EXTRA_CHANGED),44)
        self.assertEqual(len(role.selected.EXTRA_DEBUG),110)


if __name__=='__main__':unittest.main()
