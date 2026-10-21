import unittest
from unittest.mock import patch
from pyflakes.api import checkPath
import pg6438_morning_diagnostic_red as subject


class Definition(unittest.TestCase):
    def test_actual18_eight_and_pure_existing_source_prerequisite(self):
        cases, counts = subject.inventory()
        self.assertEqual((18, 8), (sum(counts.values()), len(counts)))
        self.assertEqual(6, counts['dev.codex.schubert.nk.batch.file.MorningCompletionRetirementTest'])
        self.assertIn('batch.file.MorningCompletionRetirementTest', cases['batch'])
        self.assertEqual(subject.SLOT, subject.definitions()['SLOT'])
        subject.original4054()
        for path in (subject.__file__, __file__):
            self.assertEqual(0, checkPath(path))

    def test_extra_main_cannot_enter_test_only_counterexample(self):
        with patch.object(subject.subprocess, 'check_output', return_value='src/another.java\n'):
            with self.assertRaisesRegex(ValueError, 'every Main fixed'):
                subject.guard_source('HEAD')


if __name__ == '__main__':
    unittest.main()
