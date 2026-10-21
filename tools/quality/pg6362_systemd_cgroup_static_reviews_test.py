import copy
import unittest
from unittest.mock import patch
from pyflakes.api import checkPath
import pg6362_systemd_cgroup_static_reviews as subject


class Definition(unittest.TestCase):
    def test_exact27_original_refs_without_actual_native_invocation(self):
        rows, value = subject.calculate()
        self.assertEqual(27, len(rows))
        self.assertEqual({'REQUIRED_CONTRACT': 884, 'CONTEXT_NOT_APPLICABLE': 262,
                          'FALSE_POSITIVE': 32, 'NOT_REVIEWED_CURRENT_SOURCE': 164,
                          'SOURCE_REBOUND_CURRENT_WHOLE_PENDING': 14}, value['statusCounts'])
        self.assertEqual(0, value['testsExecuted']); self.assertFalse(value['F03Accepted'])
        for row in rows:
            self.assertTrue(row['rawWarningRetained']); self.assertTrue(row['currentWholeCaseRefs'])
            self.assertFalse(row['actualRuntimeProven'])
        for path in (subject.__file__, __file__):
            self.assertEqual(0, checkPath(path))

    def test_missing_unknown_ffi_boundary_is_not_silently_accepted(self):
        changed = copy.deepcopy(subject.SPEC); del changed['LinuxSystemdSession'][(524, subject.G)]
        with patch.object(subject, 'SPEC', changed), self.assertRaisesRegex(ValueError, 'all27'):
            subject.calculate()


if __name__ == '__main__':
    unittest.main()
