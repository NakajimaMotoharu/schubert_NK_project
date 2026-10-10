import sys
import types
import unittest
from unittest.mock import patch
from pg1245_fresh_completed_capture_v2 import configuration_source, payload

class Full32CaptureTest(unittest.TestCase):
    def test_actual_qualified_full32_empty_property_and_close_failures(self):
        ns={};exec(compile(configuration_source(),'<actual frozen full32>','exec'),ns)
        events=[]
        class Array(list):signature='(sasbttttuii)'
        stop=Array();close_error=None
        class Bus:
            def get_object(self,*args):return self
            def GetUnit(self,u):events.append('GetUnit');return '/literal'
            def GetAll(self,i):events.append('GetAll');return {'ExecStop':stop}
            def close(self):
                events.append('close')
                if close_error:raise close_error
        raw=''.join(k+'=\n'for k in sorted(ns['FIELDS']-{'ExecStop'}))
        dbus=types.SimpleNamespace(SystemBus=lambda private:Bus(),Interface=lambda o,i:o,Array=Array)
        with patch.dict(sys.modules,{'dbus':dbus}):
            v=ns['complete_configuration'](raw,'literal.service')
            self.assertEqual(len(v),32);self.assertEqual(v['ExecStop'],'');self.assertEqual(events,['GetUnit','GetAll','close'])
            for bad in [None,[],Array([1])]:
                stop=bad
                with self.assertRaises(ValueError):ns['complete_configuration'](raw,'literal.service')
            stop=Array();stop.signature='foreign'
            with self.assertRaises(ValueError):ns['complete_configuration'](raw,'literal.service')
            stop=Array();close_error=OSError('unknown close')
            with self.assertRaises(OSError):ns['complete_configuration'](raw,'literal.service')
            close_error=None
            with self.assertRaises(ValueError):ns['complete_configuration'](raw.replace('Id=\n',''),'literal.service')
        compile(payload(),'<actual whole generated capture>','exec')

if __name__=='__main__':unittest.main()
