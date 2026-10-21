import unittest
from unittest.mock import patch
import finite_selected_profile as profile
import pg6646_local_audit_selected as p


class LocalAuditDefinitionTest(unittest.TestCase):
    def test_exact_declarations_compile_first(self):
        for phase,expected in (('red',(16,8)),('green',(31,11))):
            _,counts=p.inventory(phase);self.assertEqual(expected,(sum(counts.values()),len(counts)))
            raw=profile.runner(*expected,p.TARGETS)
            self.assertLess(raw.index("['-DskipTests'"),raw.index("['-Dtest='"))

    def test_three_predetermined_assertions_two_later_not_run(self):
        with patch.object(p.original,'inspect') as inspect,patch.object(p.original,'publish',return_value={}):p.read_red()
        args=inspect.call_args.args;self.assertEqual((14,6),args[2]);self.assertEqual(3,len(args[3]));self.assertEqual(2,args[5])
        self.assertEqual({'expected: <true> but was: <false>'},set(args[3].values()))

    def test_changed_main_before_red_is_rejected(self):
        with patch.object(p.subprocess,'check_call',return_value=0),patch.object(p.subprocess,'check_output',return_value='unexpected Main'):
            with self.assertRaises(ValueError):p.guard_source('fixture','red')


if __name__=='__main__':unittest.main()
