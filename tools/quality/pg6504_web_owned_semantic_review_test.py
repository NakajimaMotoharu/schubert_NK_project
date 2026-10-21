import copy
import unittest
from unittest.mock import patch
from pyflakes.api import checkPath
import pg6504_web_owned_semantic_review as subject


class Applicability(unittest.TestCase):
    def test_all_twelve_have_distinct_reason_current_methods_and_no_native_promotion(self):
        decisions, value = subject.calculate()
        self.assertEqual(12, len(decisions))
        self.assertEqual(12, len({r['reason'] for r in decisions}))
        self.assertEqual({'SOURCE_REBOUND_CURRENT_WHOLE_PENDING':1338,
            'NOT_REVIEWED_CURRENT_SOURCE':11,'REQUIRED_CONTRACT':12},value['statusCounts'])
        self.assertFalse(value['F03Accepted'])
        for row in decisions:
            self.assertTrue(row['rawWarningRetained'])
            self.assertTrue(row['currentWholeJoinPending'])
            self.assertEqual([],row['currentWholeCaseRefs'])
            self.assertFalse(row['nativeRootOrAuthorizationProven'])
            self.assertTrue(row['originalSelectedCaseRefs'])
        self.assertEqual(0,checkPath(subject.__file__))

    def test_unknown_span_or_missing_genuine_proof_cannot_be_generic_approval(self):
        decisions, _ = subject.calculate(); row = copy.deepcopy(decisions[0])
        row['rule'] = 'UnknownRule'
        with self.assertRaises(ValueError): subject.site(row,(subject.ROOT/subject.MAIN).read_text())
        with patch.object(subject,'ORDER_SHA','0'*64):
            with self.assertRaisesRegex(ValueError,'exact original27'): subject.calculate()


if __name__ == '__main__': unittest.main()
