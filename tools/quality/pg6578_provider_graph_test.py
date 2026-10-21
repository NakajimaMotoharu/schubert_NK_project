import unittest
from unittest.mock import patch
import finite_selected_profile as profile
import pg6578_provider_graph_red as selected


class ProviderDefinitionTest(unittest.TestCase):
    def test_exact_inventory_and_compile_first(self):
        _,counts=selected.inventory();self.assertEqual((15,8),(sum(counts.values()),len(counts)))
        raw=profile.runner(15,8,selected.TARGETS)
        self.assertIn('exits==[0,0,0]',raw)
        self.assertLess(raw.index("['-DskipTests'"),raw.index("['-Dtest='"))

    def test_scope_guards(self):
        with patch.object(selected.subprocess,'check_output',side_effect=[selected.TEST,b'']):selected.guard_source('fixture')
        with patch.object(selected.subprocess,'check_output',return_value='unexpected Main'):
            with self.assertRaises(ValueError):selected.guard_source('fixture')

    def test_only_two_purposeful_existing_original_assertions(self):
        with patch.object(selected.original,'inspect') as inspect,patch.object(selected.original,'publish',return_value={'actualExit':0}):
            selected.read_red()
        args=inspect.call_args.args
        self.assertEqual((9,5),args[2]);self.assertEqual(2,len(args[3]));self.assertEqual({selected.TEST},args[4])
        self.assertTrue(all(v=='Expected java.lang.AssertionError to be thrown, but nothing was thrown.' for v in args[3].values()))


if __name__=='__main__':unittest.main()
