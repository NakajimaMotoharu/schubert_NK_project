import copy
import unittest
from unittest.mock import patch
from pyflakes.api import checkPath
import pg6422_web_frame_static_reviews as subject


class Definition(unittest.TestCase):
    def test_actual_five_source_spans_preserve1358_and_pending_whole(self):
        rows, value = subject.calculate()
        self.assertEqual(5, len(rows))
        self.assertEqual({'SOURCE_REBOUND_CURRENT_WHOLE_PENDING': 1219, 'NOT_REVIEWED_CURRENT_SOURCE': 134,
                          'REQUIRED_CONTRACT': 5}, value['statusCounts'])
        self.assertEqual(1358, value['rawFindings']); self.assertFalse(value['F03Accepted'])
        self.assertEqual(0, value['testsExecuted'])
        self.assertTrue(all(r['currentWholeJoinPending'] and r['plannedCurrentWholeCaseClasses'] for r in rows))
        for path in (subject.__file__, __file__):
            self.assertEqual(0, checkPath(path))

    def test_missing_diagnostic_error_span_fails_closed(self):
        spec = copy.deepcopy(subject.SPEC); del spec['WebRuntimeExecution'][(64, subject.G)]
        with patch.object(subject, 'SPEC', spec), self.assertRaisesRegex(ValueError, 'all5'):
            subject.calculate()


if __name__ == '__main__':
    unittest.main()
