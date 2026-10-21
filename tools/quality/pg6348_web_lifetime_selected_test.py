import unittest
from unittest.mock import patch
from pyflakes.api import check, checkPath
import pg6348_web_lifetime_selected as subject
import pg6350_web_lifetime_qualification as qualification


class Definition(unittest.TestCase):
    def test_actual18_nine_and_generated_bindings(self):
        cases, counts = subject.inventory()
        self.assertEqual((18, 9), (sum(counts.values()), len(counts)))
        self.assertIn('web.bootstrap.WebUnknownRetentionTest', cases['web'])
        self.assertNotIn('api.bootstrap.ApiProcessLifetimeTest', cases['api'])
        bindings = 'from pg6206_keeper_faults_selected import runner_source,engine,node_environment,source_test_names,inspect,targets_profile\nfrom pg6348_web_lifetime_selected import inventory\n'
        self.assertEqual(0, check(bindings+subject.runner(), '<new host fixture actual bindings>'))
        for path in (subject.__file__, qualification.__file__, __file__):
            self.assertEqual(0, checkPath(path))

    def test_source_guard_rejects_other_main_or_gate_change(self):
        with patch.object(subject.subprocess, 'check_output', side_effect=['other.java\n']):
            with self.assertRaises(ValueError):
                subject.guard_source('untrusted')
        with patch.object(subject.subprocess, 'check_output', side_effect=[subject.TEST+'\n', b'changed gate']):
            with self.assertRaises(ValueError):
                subject.guard_source('untrusted')
        with patch.object(subject.subprocess, 'check_output', side_effect=[subject.TEST+'\n', b'']):
            subject.guard_source('approved')


if __name__ == '__main__':
    unittest.main()
