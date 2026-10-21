import unittest
from unittest.mock import patch
import finite_selected_profile as profile
import pg6626_jms_secondary_selected as subject


class JmsSecondaryDefinitionTest(unittest.TestCase):
    def test_inventory_compile_before_pt(self):
        for phase,expected in subject.EXPECTED.items():
            _,counts=subject.inventory(phase)
            self.assertEqual(expected,(sum(counts.values()),len(counts)))
            raw=profile.runner(*expected,subject.TARGETS)
            self.assertLess(raw.index("['-DskipTests'"),raw.index("['-Dtest='"))
            self.assertIn('exits==[0,0,0]',raw)

    def test_red_original_assertions_and_not_run_are_separate(self):
        for phase,counts,failures,notrun in (('red-api',(9,5),2,6),('red-web',(16,6),4,2)):
            with patch.object(subject.original,'inspect') as inspect,patch.object(subject.original,'publish',return_value={}):subject.read_red(phase)
            args=inspect.call_args.args
            self.assertEqual(counts,args[2]);self.assertEqual(failures,len(args[3]))
            self.assertEqual({'expected: <true> but was: <false>'},set(args[3].values()))
            self.assertEqual(subject.TESTS,args[4]);self.assertEqual(notrun,args[5])

    def test_red_rejects_changed_main(self):
        with patch.object(subject.subprocess,'check_output',return_value='unexpected Main'):
            with self.assertRaises(ValueError):subject.guard_source('fixture','red-api')


if __name__=='__main__':unittest.main()
