import unittest
from unittest.mock import patch
import finite_selected_profile as profile
import pg6652_consumer_graph_selected as p


class ConsumerDefinitionTest(unittest.TestCase):
    def test_exact_inventory_and_compile_before_dynamic(self):
        for phase,expected in p.EXPECTED.items():
            _,counts=p.inventory(phase)
            self.assertEqual(expected,(sum(counts.values()),len(counts)))
            raw=profile.runner(*expected,p.TARGETS)
            self.assertLess(raw.index("['-DskipTests'"),raw.index("['-Dtest='"))

    def test_original_seven_predetermined_boolean_failures(self):
        for phase,total,failures,later in [('red-api',(10,5),3,6),('red-web',(14,6),4,2)]:
            with patch.object(p.original,'inspect') as inspect,patch.object(p.original,'publish',return_value={}):p.read_red(phase)
            args=inspect.call_args.args
            self.assertEqual(total,args[2]);self.assertEqual(failures,len(args[3]));self.assertEqual(later,args[5])
            self.assertEqual({'expected: <true> but was: <false>'},set(args[3].values()))

    def test_unrelated_source_change_is_not_qualified(self):
        with patch.object(p.subprocess,'check_call',return_value=0),patch.object(p.subprocess,'check_output',return_value='unrelated Main'):
            with self.assertRaises(ValueError):p.guard_source('fixture','red-api')


if __name__=='__main__':unittest.main()
