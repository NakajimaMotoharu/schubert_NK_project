import unittest
from unittest.mock import patch
import finite_selected_profile as profile
import pg6612_web_owned_attachment_selected as subject


class OwnedAttachmentDefinitionTest(unittest.TestCase):
    def test_inventory_compile_first_and_unchanged_six_gates(self):
        for phase,total,suites in (('red',18,8),('green',39,11)):
            _,counts=subject.inventory(phase)
            self.assertEqual((total,suites),(sum(counts.values()),len(counts)))
            raw=profile.runner(total,suites,subject.TARGETS)
            self.assertIn('exits==[0,0,0]',raw)
            self.assertLess(raw.index("['-DskipTests'"),raw.index("['-Dtest='"))

    def test_fixed_main_and_gates_for_red(self):
        with patch.object(subject.subprocess,'check_output',side_effect=[subject.TEST,b'']):subject.guard_source('fixture','red')
        with patch.object(subject.subprocess,'check_output',return_value='other Main'):
            with self.assertRaises(ValueError):subject.guard_source('fixture','red')

    def test_five_original_assertions_fixed_before_execution(self):
        with patch.object(subject.original,'inspect') as inspect,patch.object(subject.original,'publish',return_value={'actualExit':0}):subject.read_red()
        args=inspect.call_args.args
        self.assertEqual((16,6),args[2]);self.assertEqual(5,len(args[3]));self.assertEqual({subject.TEST},args[4]);self.assertEqual(2,args[5])
        self.assertEqual(4,list(args[3].values()).count('expected: <true> but was: <false>'))


if __name__=='__main__':unittest.main()
