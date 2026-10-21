import copy
import unittest
from unittest.mock import patch
from pyflakes.api import checkPath
import pg6354_batch_database_static_reviews as subject


class Definition(unittest.TestCase):
    def test_exact35_original_references_not_runtime_authority(self):
        rows, value = subject.calculate()
        self.assertEqual(35, len(rows))
        self.assertEqual({'REQUIRED_CONTRACT': 787, 'CONTEXT_NOT_APPLICABLE': 262,
                          'FALSE_POSITIVE': 32, 'NOT_REVIEWED_CURRENT_SOURCE': 261,
                          'SOURCE_REBOUND_CURRENT_WHOLE_PENDING': 14}, value['statusCounts'])
        self.assertEqual(0, value['testsExecuted']); self.assertFalse(value['F03Accepted'])
        for row in rows:
            self.assertTrue(row['rawWarningRetained']); self.assertTrue(row['currentWholeCaseRefs'])
            self.assertFalse(row['actualRuntimeProven'])
        for path in (subject.__file__, __file__):
            self.assertEqual(0, checkPath(path))

    def test_omitted_volatile_contract_is_not_silently_completed(self):
        changed = copy.deepcopy(subject.SPEC); del changed['MorningDatabaseSession'][(663, subject.V)]
        with patch.object(subject, 'SPEC', changed), self.assertRaisesRegex(ValueError, 'all35'):
            subject.calculate()


if __name__ == '__main__':
    unittest.main()
