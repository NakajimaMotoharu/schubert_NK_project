import unittest
import xml.etree.ElementTree as ET
from unittest.mock import patch
import finite_selected_profile as profile
import finite_original_red as red
import pg6556_auth_jdbc_selected as selected


class AuthJdbcDefinitionTest(unittest.TestCase):
    def test_inventory_compile_before_pt(self):
        _, counts = selected.inventory()
        self.assertEqual((15,8),(sum(counts.values()),len(counts)))
        raw = profile.runner(15,8,selected.TARGETS)
        self.assertIn('exits==[0,0,0]',raw)
        self.assertLess(raw.index("['-DskipTests'"),raw.index("['-Dtest='"))

    def test_source_guards(self):
        with patch.object(selected.subprocess,'check_output',side_effect=[selected.TEST,b'']):
            selected.guard_source('fixture','red')
        with patch.object(selected.subprocess,'check_output',return_value='unexpected Main'):
            with self.assertRaises(ValueError): selected.guard_source('fixture','red')
        with patch.object(selected,'RED_SOURCE',None), patch.object(selected.subprocess,'check_output',
                side_effect=['\n'.join({selected.TEST}|selected.MAINS),b'']):
            with self.assertRaisesRegex(ValueError,'oracle bytes'): selected.guard_source('fixture','green')

    def test_shared_reader_defensive_rejects(self):
        expected={('CLASS','method'):'exact'}
        red.validate_failure(('CLASS','method'),ET.Element('failure',type='AssertionFailedError',message='exact'),expected)
        for key,node in ((('OTHER','method'),ET.Element('failure',type='AssertionFailedError',message='exact')),
                         (('CLASS','method'),ET.Element('failure',type='TimeoutException',message='exact')),
                         (('CLASS','method'),ET.Element('failure',type='AssertionFailedError',message='other'))):
            with self.assertRaises(ValueError): red.validate_failure(key,node,expected)

    def test_readers_exact_parameters(self):
        with patch.object(selected.original,'inspect') as inspect, patch.object(selected.original,'publish') as publish:
            inspect.return_value={'actualExit':0};publish.return_value={'actualExit':0}
            selected.read_red()
        args=inspect.call_args.args
        self.assertEqual((9,5),args[2]);self.assertEqual(3,len(args[3]));self.assertEqual({selected.TEST},args[4])
        with patch.object(selected,'W') as w,patch.object(selected,'guard_source') as guard,patch.object(selected,'qualify') as qualify:
            w.__truediv__.return_value.__truediv__.return_value.read_bytes.return_value=b'{"source":"fixture"}'
            selected.qualify_green()
        guard.assert_called_once_with('fixture','green')
        self.assertEqual((15,8),qualify.call_args.args[3]);self.assertEqual(selected.MAINS,qualify.call_args.args[4])
        self.assertEqual((0,0,0),qualify.call_args.kwargs['expected_phase_exits'])


if __name__=='__main__':unittest.main()
