import unittest
from unittest.mock import patch
import pg6292_standalone_interrupt_context as subject


class RuleContext(unittest.TestCase):
    def test_exact16_context_reasons_without_process_or_runtime_claim(self):
        rows,value=subject.calculate()
        self.assertEqual(16,len(rows));self.assertEqual(16,len({r['findingId']for r in rows}))
        self.assertEqual(367,value['statusCounts']['NOT_REVIEWED_CURRENT_SOURCE'])
        self.assertEqual(22,value['statusCounts']['CONTEXT_NOT_APPLICABLE'])
        self.assertEqual(0,value['testsExecuted']);self.assertFalse(value['formalAccepted']);self.assertFalse(value['F03Accepted'])
        for row in rows:
            self.assertEqual('DoNotUseThreads',row['rule']);self.assertTrue(row['staticContextPremiseOnly'])
            self.assertEqual([],row['currentWholeCaseRefs']);self.assertFalse(row['actualRuntimeProven'])
            self.assertEqual(subject.RULE_SHA,row['pinnedRule']['sha256'])

    def test_different_rule_artifact_cannot_inherit_context_decision(self):
        with patch.object(subject,'RULE_SHA','0'*64),self.assertRaisesRegex(ValueError,'exact pinned7.28'):
            subject.rule_premise()


if __name__=='__main__':unittest.main()
