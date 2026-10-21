import copy
import unittest
from unittest.mock import patch
from pyflakes.api import checkPath
import pg6314_web_session_static_reviews as review


class ExplicitOrdinaryScopes(unittest.TestCase):
    def test_exact14_unique_spans_not_runtime_or_coverage_acceptance(self):
        rows,value=review.calculate()
        self.assertEqual(14,len(rows));self.assertEqual(14,len({r['findingId']for r in rows}))
        self.assertEqual(343,value['statusCounts']['NOT_REVIEWED_CURRENT_SOURCE'])
        self.assertEqual(34,value['statusCounts']['REQUIRED_CONTRACT'])
        self.assertEqual(980,value['statusCounts']['SOURCE_REBOUND_CURRENT_WHOLE_PENDING'])
        for row in rows:
            self.assertFalse(row['actualRuntimeProven']);self.assertFalse(row['formalAccepted'])
            self.assertTrue(row['currentWholeJoinPending']);self.assertEqual([],row['currentWholeCaseRefs'])
            self.assertTrue(row['plannedCurrentWholeCaseClasses']);self.assertTrue(row['rawWarningRetained'])
        self.assertEqual(0,value['testsExecuted']);self.assertFalse(value['F03Accepted'])
        for path in (review.__file__,__file__):self.assertEqual(0,checkPath(path))

    def test_missing_one_explicit_span_is_rejected(self):
        spec=copy.deepcopy(review.SPEC);del spec['WebRuntimeStop']
        with patch.object(review,'SPEC',spec),self.assertRaisesRegex(ValueError,'all14'):
            review.calculate()


if __name__=='__main__':unittest.main()
