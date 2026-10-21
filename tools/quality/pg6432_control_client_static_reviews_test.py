import copy
import unittest
from unittest.mock import patch
from pyflakes.api import checkPath
import pg6432_control_client_static_reviews as subject


class Definition(unittest.TestCase):
    def test_exact41_do_not_promote_unreviewed_or_native(self):
        rows, value = subject.calculate()
        self.assertEqual(41, len(rows))
        self.assertEqual({'SOURCE_REBOUND_CURRENT_WHOLE_PENDING': 12,
                          'CONTEXT_NOT_APPLICABLE': 264, 'FALSE_POSITIVE': 32,
                          'NOT_REVIEWED_CURRENT_SOURCE': 61, 'REQUIRED_CONTRACT': 989}, value['statusCounts'])
        self.assertEqual(1358, value['rawFindings'])
        self.assertFalse(value['F03Accepted'])
        self.assertEqual(0, value['testsExecuted'])
        self.assertTrue(all(r['currentWholeJoinPending'] and not r['actualRuntimeProven'] for r in rows))
        for path in (subject.__file__, __file__):
            self.assertEqual(0, checkPath(path))

    def test_missing_unknown_or_stream_boundary_rejects(self):
        spec = copy.deepcopy(subject.SPEC)
        del spec['MaintenanceUnitStopClient'][(207, subject.G)]
        with patch.object(subject, 'SPEC', spec), self.assertRaisesRegex(ValueError, 'all41'):
            subject.calculate()


if __name__ == '__main__':
    unittest.main()
