import unittest
from unittest.mock import patch
import finite_selected_profile as profile
import pg6570_jdbc_attachment_selected as selected


class AttachmentDefinitionTest(unittest.TestCase):
    def test_inventories_compile_first(self):
        for phase,expected in (('red',(15,8)),('green',(31,12))):
            _,counts=selected.inventory(phase)
            self.assertEqual(expected,(sum(counts.values()),len(counts)))
            raw=profile.runner(*expected,selected.TARGETS)
            self.assertIn('exits==[0,0,0]',raw)
            self.assertLess(raw.index("['-DskipTests'"),raw.index("['-Dtest='"))

    def test_guard_scope_and_early_green(self):
        with patch.object(selected.subprocess,'check_output',side_effect=[selected.TEST,b'']):
            selected.guard_source('fixture','red')
        with patch.object(selected.subprocess,'check_output',return_value='unrelated Main'):
            with self.assertRaises(ValueError):selected.guard_source('fixture','red')
        with patch.object(selected,'RED_SOURCE',None),patch.object(selected.subprocess,'check_output',
                side_effect=['\n'.join({selected.TEST}|selected.MAINS),b'']):
            with self.assertRaisesRegex(ValueError,'Test bytes'):selected.guard_source('fixture','green')

    def test_original_reader_scopes(self):
        with patch.object(selected.original,'inspect') as inspect,patch.object(selected.original,'publish',return_value={'actualExit':0}):
            selected.read_red()
        self.assertEqual((9,5),inspect.call_args.args[2]);self.assertEqual(1,len(inspect.call_args.args[3]))
        with patch.object(selected,'W') as w,patch.object(selected,'guard_source') as guard,patch.object(selected,'qualify') as qualify:
            w.__truediv__.return_value.__truediv__.return_value.read_bytes.return_value=b'{"source":"fixture"}'
            selected.qualify_green()
        guard.assert_called_once_with('fixture','green')
        self.assertEqual((31,12),qualify.call_args.args[3]);self.assertEqual(selected.MAINS,qualify.call_args.args[4])
        self.assertEqual((0,0,0),qualify.call_args.kwargs['expected_phase_exits'])


if __name__=='__main__':unittest.main()
