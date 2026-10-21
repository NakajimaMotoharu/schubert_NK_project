import copy
import unittest
from unittest.mock import patch
from pyflakes.api import checkPath
import pg6344_question_storage_static_reviews as subject


class Definition(unittest.TestCase):
    def test_exact15_current_owner_spans_preserve_unknowns_and_original_inputs(self):
        rows,value=subject.calculate()
        self.assertEqual(15,len(rows));self.assertEqual(15,len({r['findingId']for r in rows}))
        self.assertEqual({'SOURCE_REBOUND_CURRENT_WHOLE_PENDING':969,'REQUIRED_CONTRACT':61,
            'CONTEXT_NOT_APPLICABLE':9,'NOT_REVIEWED_CURRENT_SOURCE':317},value['statusCounts'])
        for row in rows:
            self.assertTrue(row['rawWarningRetained']);self.assertFalse(row['actualRuntimeProven'])
            self.assertTrue(row['currentWholeJoinPending']);self.assertEqual([],row['currentWholeCaseRefs'])
            self.assertTrue(row['plannedCurrentWholeCaseClasses'])
        self.assertFalse(value['F03Accepted']);self.assertEqual(0,value['testsExecuted'])
        for path in (subject.__file__,__file__):self.assertEqual(0,checkPath(path))

    def test_missing_exact_collision_predicate_is_rejected(self):
        spec=copy.deepcopy(subject.SPEC);del spec['QuestionSubmissionService'][(410,subject.I)]
        with patch.object(subject,'SPEC',spec),self.assertRaisesRegex(ValueError,'all15'):
            subject.calculate()


if __name__=='__main__':unittest.main()
