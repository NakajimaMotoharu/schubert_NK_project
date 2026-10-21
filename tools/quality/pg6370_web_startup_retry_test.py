import unittest
from unittest.mock import patch
from pyflakes.api import check, checkPath
import pg6370_web_startup_retry as subject
import pg6372_web_startup_retry_qualification as qualification


class Definition(unittest.TestCase):
    def test_actual54_interrupted_original_and_actual_bindings(self):
        _, counts = subject.inventory(); self.assertEqual((54, 15), (sum(counts.values()), len(counts)))
        subject.interrupted()
        bindings = 'from pg6206_keeper_faults_selected import runner_source,engine,node_environment,source_test_names,inspect,targets_profile\nfrom pg6370_web_startup_retry import inventory\n'
        self.assertEqual(0, check(bindings+subject.runner(), '<new54 corrected actual bindings>'))
        for path in (subject.__file__, qualification.__file__, __file__):
            self.assertEqual(0, checkPath(path))

    def test_any_main_or_unrelated_test_change_fails(self):
        with patch.object(subject.subprocess, 'check_output', return_value='unrelated.java\n'):
            with self.assertRaises(ValueError):
                subject.guard_source('untrusted')
        with patch.object(subject.subprocess, 'check_output', side_effect=['\n'.join(sorted(subject.TESTS))+'\n', b'changed gate']):
            with self.assertRaises(ValueError):
                subject.guard_source('untrusted')


if __name__ == '__main__':
    unittest.main()
