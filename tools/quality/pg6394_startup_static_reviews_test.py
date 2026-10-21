import copy
import unittest
from unittest.mock import patch
from pyflakes.api import checkPath
import pg6394_startup_static_reviews as subject


class Definition(unittest.TestCase):
    def test_changed19_remain_separate_from_whole_pt_and_native(self):
        rows, value = subject.calculate()
        self.assertEqual(19, len(rows))
        self.assertEqual({'SOURCE_REBOUND_CURRENT_WHOLE_PENDING': 1175, 'NOT_REVIEWED_CURRENT_SOURCE': 161,
                          'REQUIRED_CONTRACT': 16, 'CONTEXT_NOT_APPLICABLE': 3}, value['statusCounts'])
        self.assertEqual(0, value['testsExecuted']); self.assertFalse(value['F03Accepted'])
        for row in rows:
            self.assertTrue(row['rawWarningRetained']); self.assertEqual([], row['currentWholeCaseRefs'])
            self.assertTrue(row['currentWholeJoinPending']); self.assertFalse(row['actualRuntimeProven'])
        for path in (subject.__file__, __file__):
            self.assertEqual(0, checkPath(path))

    def test_missing_unknown_error_span_cannot_complete19(self):
        spec = copy.deepcopy(subject.SPEC); del spec['WebLogApplicationRuntime'][(287, subject.G)]
        with patch.object(subject, 'SPEC', spec), self.assertRaisesRegex(ValueError, 'all19'):
            subject.calculate()


if __name__ == '__main__':
    unittest.main()
