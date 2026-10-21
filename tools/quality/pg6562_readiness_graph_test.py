import unittest
from unittest.mock import patch
import finite_selected_profile as profile
import pg6562_readiness_graph_selected as selected


class ReadinessDefinitionTest(unittest.TestCase):
    def test_red_inventories_and_green_compile_plan(self):
        for phase in ('api-red','web-red'):
            _, counts=selected.inventory(phase)
            self.assertEqual((15,8),(sum(counts.values()),len(counts)))
        for expected in ((15,8),(24,11)):
            raw=profile.runner(*expected,selected.TARGETS)
            self.assertIn('exits==[0,0,0]',raw)
            self.assertLess(raw.index("['-DskipTests'"),raw.index("['-Dtest='"))
        _, green=selected.inventory('green')
        self.assertEqual((24,11),(sum(green.values()),len(green)))

    def test_source_scope_and_premature_green_guards(self):
        with patch.object(selected.subprocess,'check_output',side_effect=['\n'.join(selected.TESTS),b'']):
            selected.guard_source('fixture','api-red')
        with patch.object(selected.subprocess,'check_output',return_value='unexpected Main'):
            with self.assertRaises(ValueError):selected.guard_source('fixture','web-red')
        changes='\n'.join(selected.TESTS|selected.GRAPH_TESTS|selected.MAINS)
        with patch.object(selected,'RED_SOURCE',None),patch.object(selected.subprocess,'check_output',side_effect=[changes,b'']):
            with self.assertRaisesRegex(ValueError,'Test bytes'):selected.guard_source('fixture','green')

    def test_both_red_reader_scopes_and_different_source_reject(self):
        def value(run,guard,counts,expected,tests,notrun):
            self.assertEqual(2,len(expected));self.assertEqual(selected.TESTS,tests)
            self.assertIn((counts,notrun),(((9,5),6),((13,6),2)))
            return dict(source='fixture',TestHashes={'x':'hash'},expectedFailures=list(expected))
        with patch.object(selected.original,'inspect',side_effect=value),patch.object(selected.original,'publish',return_value={'actualExit':0}):
            selected.read_red()
        first=dict(source='a',TestHashes={'x':'hash'});second=dict(source='b',TestHashes={'x':'hash'})
        with patch.object(selected.original,'inspect',side_effect=[first,second]):
            with self.assertRaisesRegex(ValueError,'same original'):selected.read_red()

    def test_green_reader_exact_four_main_and_three_phases(self):
        with patch.object(selected,'W') as w,patch.object(selected,'guard_source') as guard,patch.object(selected,'qualify') as qualify:
            w.__truediv__.return_value.__truediv__.return_value.read_bytes.return_value=b'{"source":"fixture"}'
            selected.qualify_green()
        guard.assert_called_once_with('fixture','green')
        self.assertEqual((24,11),qualify.call_args.args[3]);self.assertEqual(selected.MAINS,qualify.call_args.args[4])
        self.assertEqual((0,0,0),qualify.call_args.kwargs['expected_phase_exits'])


if __name__=='__main__':unittest.main()
