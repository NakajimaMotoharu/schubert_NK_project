import inspect
import unittest
from pyflakes.api import check, checkPath
import pg6364_web_startup_green as subject
import pg6366_web_startup_qualification as qualification


class Definition(unittest.TestCase):
    def test_actual54_original_red_and_two_main_only(self):
        _, counts = subject.inventory()
        self.assertEqual((54, 15), (sum(counts.values()), len(counts)))
        self.assertEqual(2, len(subject.MAIN)); subject.reproduced()
        raw = subject.red.runner().replace('runner_source(20,10,target_count=16)', 'runner_source(54,15,target_count=16)').replace('pg6360-web-startup-red-v1', 'pg6364-web-startup-selected-v1').replace('def run_red():', 'def run_green():')
        bindings = 'from pg6206_keeper_faults_selected import runner_source,engine,node_environment,source_test_names,inspect,targets_profile\nfrom pg6364_web_startup_green import inventory\n'
        self.assertEqual(0, check(bindings+raw, '<related54 actual bindings>'))
        self.assertIn('(54, 15)', inspect.getsource(qualification.main))
        for path in (subject.__file__, qualification.__file__, __file__):
            self.assertEqual(0, checkPath(path))


if __name__ == '__main__':
    unittest.main()
