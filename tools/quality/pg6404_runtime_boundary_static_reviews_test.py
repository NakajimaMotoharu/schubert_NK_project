import copy
import unittest
from unittest.mock import patch
from pyflakes.api import checkPath
import pg6404_runtime_boundary_static_reviews as subject


class Definition(unittest.TestCase):
    def test_exact25_source_spans_no_real_ops_or_old_pt_success(self):
        rows, value = subject.calculate()
        self.assertEqual(25, len(rows))
        self.assertEqual({'SOURCE_REBOUND_CURRENT_WHOLE_PENDING': 1175, 'NOT_REVIEWED_CURRENT_SOURCE': 136,
                          'REQUIRED_CONTRACT': 41, 'CONTEXT_NOT_APPLICABLE': 3}, value['statusCounts'])
        self.assertEqual(0, value['testsExecuted']); self.assertFalse(value['F03Accepted'])
        self.assertTrue(all(r['currentWholeJoinPending'] and not r['actualRuntimeProven'] for r in rows))
        self.assertNotIn('WebRuntimeExecution', subject.SPEC)
        for path in (subject.__file__, __file__):
            self.assertEqual(0, checkPath(path))

    def test_missing_provider_error_span_cannot_complete25(self):
        spec = copy.deepcopy(subject.SPEC); del spec['WebHttpServer'][(172, subject.G)]
        with patch.object(subject, 'SPEC', spec), self.assertRaisesRegex(ValueError, 'all25'):
            subject.calculate()


if __name__ == '__main__':
    unittest.main()
