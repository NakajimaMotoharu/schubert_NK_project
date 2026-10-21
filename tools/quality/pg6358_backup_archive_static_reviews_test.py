import copy
import unittest
from unittest.mock import patch
from pyflakes.api import checkPath
import pg6358_backup_archive_static_reviews as subject


class Definition(unittest.TestCase):
    def test_exact35_original_refs_and_no_dynamic_backup(self):
        rows, value = subject.calculate()
        self.assertEqual(35, len(rows))
        self.assertEqual({'REQUIRED_CONTRACT': 857, 'CONTEXT_NOT_APPLICABLE': 262,
                          'FALSE_POSITIVE': 32, 'NOT_REVIEWED_CURRENT_SOURCE': 191,
                          'SOURCE_REBOUND_CURRENT_WHOLE_PENDING': 14}, value['statusCounts'])
        self.assertEqual(0, value['testsExecuted']); self.assertFalse(value['F03Accepted'])
        for row in rows:
            self.assertTrue(row['rawWarningRetained']); self.assertTrue(row['currentWholeCaseRefs'])
            self.assertFalse(row['actualRuntimeProven'])
        for path in (subject.__file__, __file__):
            self.assertEqual(0, checkPath(path))

    def test_missing_pipeline_factory_quarantine_reason_is_rejected(self):
        changed = copy.deepcopy(subject.SPEC); del changed['BackupArchiveProcess'][(551, subject.G)]
        with patch.object(subject, 'SPEC', changed), self.assertRaisesRegex(ValueError, 'all35'):
            subject.calculate()


if __name__ == '__main__':
    unittest.main()
