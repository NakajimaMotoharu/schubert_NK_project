"""Independent typed-empty proof/close-failure propagation, no PID1 mutation."""
import ast
import sys
import types
import unittest
from unittest.mock import patch
from pg775_configuration import FIELDS,configuration_value
from pg776_failure_full import ADDITIONAL,source


class Test(unittest.TestCase):
    def test_actual_empty_only_and_owned_close(self):
        definition=ast.parse(ADDITIONAL)
        events=[]
        class Array(list):signature='(sasbttttuii)'
        stop=Array();error=None;close_error=None
        class Bus:
            def get_object(self,*args):return self
            def GetUnit(self,u):events.append('getunit');return '/literal/unit'
            def GetAll(self,i):
                events.append('getall')
                if error:raise error
                return {'ExecStop':stop}
            def close(self):
                events.append('close')
                if close_error:raise close_error
        env={'configuration_value':configuration_value};exec(compile(definition,'<literal typed proof>','exec'),env)
        raw=''.join(k+'=\n'for k in sorted(FIELDS-{'ExecStop'}))
        mock=types.SimpleNamespace(SystemBus=lambda private:Bus(),Interface=lambda o,i:o,Array=Array)
        with patch.dict(sys.modules,{'dbus':mock}):
            self.assertEqual('',env['complete_configuration'](raw,'literal.service')['ExecStop']);self.assertEqual(['getunit','getall','close'],events)
            for bad in (None,[],Array([1])):
                stop=bad
                with self.assertRaises(ValueError):env['complete_configuration'](raw,'literal.service')
            stop=Array();stop.signature='foreign'
            with self.assertRaises(ValueError):env['complete_configuration'](raw,'literal.service')
            stop=Array();error=OSError('literal failure')
            with self.assertRaises(OSError):env['complete_configuration'](raw,'literal.service')
            error=None;close_error=OSError('literal close unknown')
            with self.assertRaises(OSError):env['complete_configuration'](raw,'literal.service')
            close_error=None
            with self.assertRaises(ValueError):env['complete_configuration'](raw.replace('Id=\n',''),'literal.service')
        ast.parse(source());self.assertIn('pg776-failure-full758-v1',source())


if __name__=='__main__':unittest.main()
