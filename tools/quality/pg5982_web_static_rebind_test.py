import unittest
from pg5982_web_static_rebind import references


class PendingReferenceProvenanceTest(unittest.TestCase):
    def test_only_semantic_pending_refs_not_whole_pass(self):
        ref = {'class':'test.Case','caseNameSha256':'a'*64}; row = {'plannedCurrentTestRefs':[ref], 'currentWholeCaseRefs':[]}
        self.assertEqual([ref], references(row))
        self.assertEqual([], references({'priorDisposition':'CONTEXT_NOT_APPLICABLE','plannedCurrentTestRefs':[],'currentWholeCaseRefs':[]}))
        for wrong in ({}, {**row,'currentWholeCaseRefs':[ref]}, {**row,'plannedCurrentTestRefs':[{**ref,'result':'PASS'}]}, {**row,'plannedCurrentTestRefs':[{**ref,'caseNameSha256':'short'}]}):
            with self.assertRaises(ValueError):
                references(wrong)
        for prior in ('REQUIRED_CONTRACT','FALSE_POSITIVE',None):
            with self.assertRaises(ValueError):
                references({'priorDisposition':prior,'plannedCurrentTestRefs':[],'currentWholeCaseRefs':[]})


if __name__ == '__main__':
    unittest.main()
