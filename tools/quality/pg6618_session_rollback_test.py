import unittest
from unittest.mock import patch
import finite_selected_profile as profile
import pg6618_session_rollback_selected as subject


class SessionRollbackDefinitionTest(unittest.TestCase):
    def test_complete_inventory_and_compile_first(self):
        for phase,total,suites in (('red',15,8),('green',33,12)):
            _,counts=subject.inventory(phase)
            self.assertEqual((total,suites),(sum(counts.values()),len(counts)))
            raw=profile.runner(total,suites,subject.TARGETS)
            self.assertIn('exits==[0,0,0]',raw)
            self.assertLess(raw.index("['-DskipTests'"),raw.index("['-Dtest='"))

    def test_red_main_and_build_are_fixed(self):
        with patch.object(subject.subprocess,'check_output',side_effect=[subject.TEST,b'']):subject.guard_source('fixture','red')
        with patch.object(subject.subprocess,'check_output',return_value='unexpected Main'):
            with self.assertRaises(ValueError):subject.guard_source('fixture','red')

    def test_predetermined_one_assertion_and_two_later_not_run(self):
        with patch.object(subject.original,'inspect') as inspect,patch.object(subject.original,'publish',return_value={'actualExit':0}):subject.read_red()
        args=inspect.call_args.args
        self.assertEqual((13,6),args[2]);self.assertEqual(1,len(args[3]));self.assertEqual({subject.TEST},args[4]);self.assertEqual(2,args[5])


if __name__=='__main__':unittest.main()
