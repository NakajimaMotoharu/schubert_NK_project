import unittest
from unittest.mock import patch
from pyflakes.api import checkPath
import pg6440_morning_diagnostic_green as subject
import pg6442_morning_diagnostic_qualification as qualifier


class Definition(unittest.TestCase):
    def test_actual23_ten_and_pure_target(self):
        _, counts = subject.inventory()
        self.assertEqual((23, 10), (sum(counts.values()), len(counts)))
        self.assertEqual({'batch': ['batch/file/MorningStartupLaunchOwner$CompletionProgress']}, subject.definitions()['TARGETS'])
        for path in (subject.__file__, qualifier.__file__, __file__):
            self.assertEqual(0, checkPath(path))

    def test_absent_genuine_red_cannot_qualify_or_launch(self):
        with patch.object(subject, 'RED_SOURCE', None), self.assertRaisesRegex(ValueError, 'genuine counterexample'):
            subject.guard_source('HEAD')


if __name__ == '__main__':
    unittest.main()
