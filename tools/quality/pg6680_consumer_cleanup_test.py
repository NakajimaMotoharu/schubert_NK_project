import unittest
from unittest.mock import patch
import finite_selected_profile as profile
import pg6680_consumer_cleanup_selected as p


class CleanupDefinitionTest(unittest.TestCase):
    def test_exact_inventory_and_all_six_compile_before_pt(self):
        for phase,expected in p.EXPECTED.items():
            _,counts=p.inventory(phase);self.assertEqual(expected,(sum(counts.values()),len(counts)))
            raw=profile.runner(*expected,p.TARGETS)
            self.assertLess(raw.index("['-DskipTests'"),raw.index("['-Dtest='"))

    def test_five_independent_explicit_target_messages_not_unknown_fixture_failure(self):
        for phase,counts,failures,later in [('red-api',(10,5),4,6),('red-web',(12,6),1,2)]:
            with patch.object(p.original,'inspect') as inspect,patch.object(p.original,'publish',return_value={}):p.read_red(phase)
            args=inspect.call_args.args
            self.assertEqual(counts,args[2]);self.assertEqual(failures,len(args[3]));self.assertEqual(later,args[5])
            self.assertTrue(all(v.startswith('CONS333-') and '==> expected: <true> but was: <false>' in v for v in args[3].values()))

    def test_unrelated_source_change_cannot_enter_red(self):
        with patch.object(p.subprocess,'check_call',return_value=0),patch.object(p.subprocess,'check_output',return_value='unknown Main'):
            with self.assertRaises(ValueError):p.guard_source('fixture','red-api')


if __name__=='__main__':unittest.main()
