import copy
import unittest
from unittest.mock import patch
from pyflakes.api import checkPath
import pg6356_shared_boundary_static_reviews as subject


class Definition(unittest.TestCase):
    def test_exact35_current_original_case_join_and_no_runtime_claim(self):
        rows, value = subject.calculate()
        self.assertEqual(35, len(rows))
        self.assertEqual({'REQUIRED_CONTRACT': 822, 'CONTEXT_NOT_APPLICABLE': 262,
                          'FALSE_POSITIVE': 32, 'NOT_REVIEWED_CURRENT_SOURCE': 226,
                          'SOURCE_REBOUND_CURRENT_WHOLE_PENDING': 14}, value['statusCounts'])
        self.assertEqual(0, value['testsExecuted']); self.assertFalse(value['F03Accepted'])
        for row in rows:
            self.assertTrue(row['rawWarningRetained']); self.assertTrue(row['currentWholeCaseRefs'])
            self.assertFalse(row['actualRuntimeProven'])
        for path in (subject.__file__, __file__):
            self.assertEqual(0, checkPath(path))

    def test_missing_decoded_ownership_transfer_reason_is_rejected(self):
        changed = copy.deepcopy(subject.SPEC); del changed['InspectorAesCredential']
        with patch.object(subject, 'SPEC', changed), self.assertRaisesRegex(ValueError, 'all35'):
            subject.calculate()


if __name__ == '__main__':
    unittest.main()
