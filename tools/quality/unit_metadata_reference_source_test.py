import sys
import types
import unittest
from unittest.mock import patch
from unit_metadata_reference_source import scope


class Ref(unittest.TestCase):
    def test_all_ten_lifo_close_normal_body_failure_partial_acquire_and_unref_failure(self):
        units=['fixture'+str(i)+'.service'for i in range(10)]
        for fail in ['none','body','ref','unref']:
            events=[];failure=RuntimeError('independent fixed failure')
            def record(kind,name=None):
                events.append((kind,name))
                if(fail=='ref'and kind=='ref'and name==units[3])or(fail=='unref'and kind=='unref'):raise failure
            manager=types.SimpleNamespace(LoadUnit=lambda u:record('load',u),RefUnit=lambda u:record('ref',u),UnrefUnit=lambda u:record('unref',u))
            bus=types.SimpleNamespace(get_object=lambda *args:object(),close=lambda:record('close'))
            module=types.SimpleNamespace(SystemBus=lambda private:bus,Interface=lambda *args:manager)
            def body():
                record('body')
                if fail=='body':raise failure
            ns={'expected':{'units':dict.fromkeys(units)},'body':body}
            with patch.dict(sys.modules,{'dbus':module}):
                if fail=='none':exec(scope('body()'),ns)
                else:
                    with self.assertRaises(RuntimeError)as found:exec(scope('body()'),ns)
                    self.assertIs(failure,found.exception)
            self.assertEqual(('close',None),events[-1])
            if fail in ['none','body']:self.assertEqual(list(reversed(units)),[u for k,u in events if k=='unref'])
            if fail=='ref':self.assertEqual(list(reversed(units[:3])),[u for k,u in events if k=='unref']);self.assertNotIn(('body',None),events)


if __name__=='__main__':unittest.main()
