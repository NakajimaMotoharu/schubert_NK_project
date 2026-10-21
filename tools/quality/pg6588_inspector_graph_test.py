import unittest
from unittest.mock import patch
import pg6588_inspector_graph_selected as subject
import finite_selected_profile as profile


class InspectorDefinitionTest(unittest.TestCase):
    def test_exact_inventory_and_compile_first(self):
        for phase,total,suites in (('red',21,8),('green',60,12)):
            _,counts=subject.inventory(phase)
            self.assertEqual((total,suites),(sum(counts.values()),len(counts)))
            raw=profile.runner(total,suites,subject.TARGETS)
            self.assertIn('exits==[0,0,0]',raw)
            self.assertLess(raw.index("['-DskipTests'"),raw.index("['-Dtest='"))

    def test_red_preserves_all_main_and_gates(self):
        with patch.object(subject.subprocess,'check_output',side_effect=[subject.TEST,b'']):subject.guard_source('fixture','red')
        with patch.object(subject.subprocess,'check_output',return_value='unexpected Main'):
            with self.assertRaises(ValueError):subject.guard_source('fixture','red')

    def test_original_expected_failures_not_updated_from_actual(self):
        with patch.object(subject.original,'inspect') as inspect,patch.object(subject.original,'publish',return_value={'actualExit':0}):
            subject.read_red()
        args=inspect.call_args.args
        self.assertEqual((15,5),args[2]);self.assertEqual(7,len(args[3]));self.assertEqual(6,args[5])
        self.assertEqual({subject.TEST},args[4])


if __name__=='__main__':unittest.main()
