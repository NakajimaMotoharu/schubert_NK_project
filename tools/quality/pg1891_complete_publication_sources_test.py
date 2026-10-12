"""Actual emitted module/consumer exports and strict two-field transport parser."""
import ast
import types
import unittest
from unittest.mock import patch
from pyflakes.api import check
from pg1891_complete_publication_sources import sources


class Complete(unittest.TestCase):
    def test_actual_full_module_has_every_consumed_attribute(self):
        actual=sources();module=types.ModuleType('actual_full_h')
        exec(compile(actual['pg1891_native_owned_stop.py'],'<actual module>','exec'),module.__dict__)
        names={n.attr for n in ast.walk(ast.parse(actual['pg1891_native_refs.py']))if isinstance(n,ast.Attribute)and isinstance(n.value,ast.Name)and n.value.id=='h'}
        self.assertIn('parent_configuration',names)
        for name in names:self.assertTrue(hasattr(module,name),name)
        self.assertEqual('/var/lib/pgpt-s1-preservation/pg1895-warning-publication-v1',str(module.ROOT))
        self.assertEqual('3d69f5af-6bac-46b1-a540-7591c4a79a0d',module.BOOT)
        for name,raw in actual.items():
            if name.endswith('.py'):self.assertEqual(0,check(raw,'<actual complete '+name+'>'))

    def test_actual_preserved_suffix_executes_real_parser_not_fixture_attribute(self):
        actual=sources();module=types.ModuleType('actual_full_parser')
        exec(actual['pg1891_native_owned_stop.py'],module.__dict__)
        for value,expected in [(b'Type=oneshot\nSuccessExitStatus=\n',{'Type':'oneshot','SuccessExitStatus':''}),(b'SuccessExitStatus=10\nType=oneshot\n',{'Type':'oneshot','SuccessExitStatus':'10'})]:
            with patch('subprocess.check_output',return_value=value)as command:
                self.assertEqual(expected,module.parent_configuration())
                command.assert_called_once_with(['/usr/bin/systemctl','show','schubert-nk-morning-controller.service','--property=Type,SuccessExitStatus'],timeout=5)
        for value in [b'',b'Type=oneshot\n',b'Type=oneshot\nType=oneshot\n',b'Type=oneshot\nSuccessExitStatus=10',b'Type=oneshot\nUnknown=10\n',b'Type=oneshot\nSuccessExitStatus=10\nOther=x\n',b'Type=\xff\nSuccessExitStatus=\n']:
            with patch('subprocess.check_output',return_value=value):
                with self.assertRaises((ValueError,UnicodeError)):module.parent_configuration()


if __name__=='__main__':unittest.main()
