import unittest
from unittest.mock import patch
from pyflakes.api import check, checkPath
import pg6360_web_startup_red as subject


class Definition(unittest.TestCase):
    def test_actual20_original18_and_generated_bindings(self):
        _, counts = subject.inventory()
        self.assertEqual((20, 10), (sum(counts.values()), len(counts)))
        subject.prior18()
        bindings = 'from pg6206_keeper_faults_selected import runner_source,engine,node_environment,source_test_names,inspect,targets_profile\nfrom pg6360_web_startup_red import inventory\n'
        self.assertEqual(0, check(bindings+subject.runner(), '<20 actual startup reproduction bindings>'))
        for path in (subject.__file__, __file__):
            self.assertEqual(0, checkPath(path))

    def test_no_extra_main_or_gate_change(self):
        with patch.object(subject.subprocess, 'check_output', side_effect=['other.java\n']):
            with self.assertRaises(ValueError):
                subject.guard_source('untrusted')
        with patch.object(subject.subprocess, 'check_output', side_effect=[subject.TEST+'\n', b'changed gate']):
            with self.assertRaises(ValueError):
                subject.guard_source('untrusted')


if __name__ == '__main__':
    unittest.main()
