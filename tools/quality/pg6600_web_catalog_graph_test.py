import unittest
from unittest.mock import patch
import finite_selected_profile as profile
import pg6600_web_catalog_graph_selected as subject


class WebCatalogDefinitionTest(unittest.TestCase):
    def test_exact_inventory_and_compile_first(self):
        for phase,total,suites in (('red',18,9),('green',38,13)):
            _,counts=subject.inventory(phase)
            self.assertEqual((total,suites),(sum(counts.values()),len(counts)))
            raw=profile.runner(total,suites,subject.TARGETS)
            self.assertIn('exits==[0,0,0]',raw)
            self.assertLess(raw.index("['-DskipTests'"),raw.index("['-Dtest='"))

    def test_red_main_and_gates_are_fixed(self):
        with patch.object(subject.subprocess,'check_output',side_effect=['\n'.join(subject.TESTS),b'']):subject.guard_source('fixture','red')
        with patch.object(subject.subprocess,'check_output',return_value='unexpected Main'):
            with self.assertRaises(ValueError):subject.guard_source('fixture','red')

    def test_predetermined_four_failures_and_not_run_are_not_promoted(self):
        with patch.object(subject.original,'inspect') as inspect,patch.object(subject.original,'publish',return_value={'actualExit':0}):subject.read_red()
        args=inspect.call_args.args
        self.assertEqual((16,7),args[2]);self.assertEqual(4,len(args[3]));self.assertEqual(subject.TESTS,args[4]);self.assertEqual(2,args[5])


if __name__=='__main__':unittest.main()
