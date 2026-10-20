import unittest
from pg6012_api_bounds_rebind import changed_reason


class DeclaredApiChangedReasonTest(unittest.TestCase):
    def test_only_declared_context_and_semantic_refs_without_old_whole_pass(self):
        old=dict(priorReason='existing standalone actor reason',priorDisposition='CONTEXT_NOT_APPLICABLE',plannedCurrentTestRefs=[],currentWholeCaseRefs=[])
        row=dict(sourcePath='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/bootstrap/ApiManagementServer.java',rule='DoNotUseThreads')
        value=changed_reason(row,old)
        self.assertTrue(value['explicitCurrentSourceRereview']);self.assertEqual([],value['currentWholeCaseRefs'])
        self.assertFalse(value['currentTypedMeasurementClaimed'])
        for bad in ({**row,'rule':'Unknown'},{**row,'sourcePath':'foreign.java'}):
            with self.assertRaises(ValueError):changed_reason(bad,old)


if __name__=='__main__':unittest.main()
