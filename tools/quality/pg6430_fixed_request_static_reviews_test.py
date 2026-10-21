import copy
import unittest
from unittest.mock import patch
from pyflakes.api import checkPath
import pg6430_fixed_request_static_reviews as subject


class Definition(unittest.TestCase):
    def test_exact17_keep_pending_source_and_all_raw(self):
        rows, value = subject.calculate()
        self.assertEqual(17, len(rows))
        self.assertEqual({'SOURCE_REBOUND_CURRENT_WHOLE_PENDING': 1217,
                          'CONTEXT_NOT_APPLICABLE': 2, 'NOT_REVIEWED_CURRENT_SOURCE': 102,
                          'REQUIRED_CONTRACT': 37}, value['statusCounts'])
        self.assertEqual(1358, value['rawFindings'])
        self.assertFalse(value['F03Accepted'])
        self.assertEqual(0, value['testsExecuted'])
        for path in (subject.__file__, __file__):
            self.assertEqual(0, checkPath(path))

    def test_missing_one_borrowed_owner_rationale_is_rejected(self):
        spec = copy.deepcopy(subject.SPEC)
        del spec['MaintenanceRunFiles'][(668, subject.R)]
        with patch.object(subject, 'SPEC', spec), self.assertRaisesRegex(ValueError, 'all17'):
            subject.calculate()


if __name__ == '__main__':
    unittest.main()
