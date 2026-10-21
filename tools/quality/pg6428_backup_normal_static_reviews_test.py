import copy
import unittest
from unittest.mock import patch
from pyflakes.api import checkPath
import pg6428_backup_normal_static_reviews as subject


class Definition(unittest.TestCase):
    def test_exact15_current_spans_keep_pending_and_raw_findings(self):
        rows, value = subject.calculate()
        self.assertEqual(15, len(rows))
        self.assertEqual({'SOURCE_REBOUND_CURRENT_WHOLE_PENDING': 1217,
                          'CONTEXT_NOT_APPLICABLE': 2, 'NOT_REVIEWED_CURRENT_SOURCE': 119,
                          'REQUIRED_CONTRACT': 20}, value['statusCounts'])
        self.assertEqual(1358, value['rawFindings'])
        self.assertEqual(0, value['testsExecuted'])
        self.assertFalse(value['F03Accepted'])
        self.assertTrue(all(r['currentWholeJoinPending'] and r['plannedCurrentWholeCaseClasses'] for r in rows))
        for path in (subject.__file__, __file__):
            self.assertEqual(0, checkPath(path))

    def test_missing_one_typed_failure_reason_rejects(self):
        spec = copy.deepcopy(subject.SPEC)
        del spec['BackupArtifactVerifier'][(566, 'AvoidInstanceofChecksInCatchClause')]
        with patch.object(subject, 'SPEC', spec), self.assertRaisesRegex(ValueError, 'all15'):
            subject.calculate()


if __name__ == '__main__':
    unittest.main()
