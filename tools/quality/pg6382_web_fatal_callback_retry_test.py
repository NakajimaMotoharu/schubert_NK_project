import inspect
import unittest
from unittest.mock import patch
from pyflakes.api import check, checkPath
import pg6382_web_fatal_callback_retry as subject
import pg6384_web_fatal_callback_retry_qualification as qualification


class Definition(unittest.TestCase):
    def test_actual22_preserved_compile_failure_and_bindings(self):
        _, counts = subject.inventory(); self.assertEqual((22, 8), (sum(counts.values()), len(counts)))
        subject.failed_compile()
        bindings = 'from pg6206_keeper_faults_selected import runner_source,engine,node_environment,source_test_names,inspect,targets_profile\nfrom pg6382_web_fatal_callback_retry import inventory\n'
        self.assertEqual(0, check(bindings+subject.runner(), '<corrected22 actual bindings>'))
        self.assertIn("'-proc:none'", inspect.getsource(subject.precompile))
        for path in (subject.__file__, qualification.__file__, __file__):
            self.assertEqual(0, checkPath(path))

    def test_other_source_or_expectation_change_fails(self):
        with patch.object(subject.subprocess, 'check_output', return_value='unexpected.java\n'):
            with self.assertRaises(ValueError):
                subject.guard_source('untrusted')
        with patch.object(subject.subprocess, 'check_output', side_effect=[subject.previous.TEST+'\n', b'old', b'changed assertion']):
            with self.assertRaises(ValueError):
                subject.guard_source('untrusted')


if __name__ == '__main__':
    unittest.main()
