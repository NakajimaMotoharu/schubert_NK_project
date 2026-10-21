import copy
import unittest
from unittest.mock import patch
from pyflakes.api import checkPath
import pg6352_ordinary_boundary_static_reviews as subject


class Definition(unittest.TestCase):
    def test_exact21_actual_original_refs_and_all_unknowns_retained(self):
        rows, value = subject.calculate()
        self.assertEqual(21, len(rows))
        self.assertEqual({'REQUIRED_CONTRACT': 752, 'CONTEXT_NOT_APPLICABLE': 262,
                          'FALSE_POSITIVE': 32, 'NOT_REVIEWED_CURRENT_SOURCE': 296,
                          'SOURCE_REBOUND_CURRENT_WHOLE_PENDING': 14}, value['statusCounts'])
        for row in rows:
            self.assertTrue(row['rawWarningRetained'])
            self.assertTrue(row['currentWholeCaseRefs'])
            self.assertFalse(row['actualRuntimeProven'])
        self.assertEqual(0, value['testsExecuted']); self.assertFalse(value['F03Accepted'])
        for path in (subject.__file__, __file__):
            self.assertEqual(0, checkPath(path))

    def test_omitted_span_and_unavailable_semantic_refs_fail(self):
        changed = copy.deepcopy(subject.SPEC); del changed['ContextHash']
        with patch.object(subject, 'SPEC', changed), self.assertRaisesRegex(ValueError, 'all21'):
            subject.calculate()
        changed = copy.deepcopy(subject.TESTS); changed['ContextHash'] = []
        with patch.object(subject, 'TESTS', changed):
            # No reference cannot be accepted merely because a source span exists.
            with self.assertRaisesRegex(ValueError, 'semantic Test'):
                subject.calculate()


if __name__ == '__main__':
    unittest.main()
