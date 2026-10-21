import unittest
from unittest.mock import patch
import finite_selected_profile as profile
import pg6690_broker_parent_selected as p


class BrokerDefinitionTest(unittest.TestCase):
    def test_exact_current_inventory_compile_first_and_owned_profile(self):
        for phase,expected in p.EXPECTED.items():
            _,counts=p.inventory(phase);self.assertEqual(expected,(sum(counts.values()),len(counts)))
            raw=profile.runner(*expected,p.TARGETS)
            self.assertLess(raw.index("['-DskipTests'"),raw.index("['-Dtest='"))

    def test_eight_explicit_target_assertions_and_original_not_run_counts(self):
        for phase,counts,n,later in [('red-api',(11,6),5,6),('red-web',(13,6),3,2)]:
            with patch.object(p.original,'inspect') as inspect,patch.object(p.original,'publish',return_value={}):p.read_red(phase)
            args=inspect.call_args.args;self.assertEqual(counts,args[2]);self.assertEqual(n,len(args[3]));self.assertEqual(later,args[5])
            self.assertTrue(all(v.startswith('FACT334') and v.endswith('==> expected: <true> but was: <false>') for v in args[3].values()))

    def test_unrelated_main_or_oracle_change_is_not_accepted(self):
        with patch.object(p.subprocess,'check_call',return_value=0),patch.object(p.subprocess,'check_output',return_value='unknown Main'):
            with self.assertRaises(ValueError):p.guard_source('fixture','red-api')


if __name__=='__main__':unittest.main()
