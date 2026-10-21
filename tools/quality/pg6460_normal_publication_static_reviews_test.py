import copy
import unittest
from unittest.mock import patch
from pyflakes.api import checkPath
import pg6460_normal_publication_static_reviews as subject


class Definition(unittest.TestCase):
    def test_actual56_keep_eleven_recovery_twelve_semantic_held(self):
        rows, value = subject.calculate()
        self.assertEqual(56, len(rows))
        self.assertEqual({'SOURCE_REBOUND_CURRENT_WHOLE_PENDING': 1294,
                          'NOT_REVIEWED_CURRENT_SOURCE': 11, 'REQUIRED_CONTRACT': 53,
                          'CONTEXT_NOT_APPLICABLE': 3}, value['statusCounts'])
        self.assertEqual(1361, value['rawFindings'])
        self.assertEqual(0, value['testsExecuted'])
        self.assertFalse(value['F03Accepted'])
        self.assertTrue(all(r['currentWholeJoinPending'] and not r['actualRuntimeProven'] for r in rows))
        for path in (subject.__file__, __file__):
            self.assertEqual(0, checkPath(path))

    def test_changed_class_thread_context_cannot_be_implicitly_imported(self):
        spec = copy.deepcopy(subject.SPEC)
        del spec['MorningStartupLaunchOwner'][(748, subject.T)]
        with patch.object(subject, 'SPEC', spec), self.assertRaisesRegex(ValueError, 'all56'):
            subject.calculate()


if __name__ == '__main__':
    unittest.main()
