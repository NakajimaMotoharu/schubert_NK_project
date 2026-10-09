"""Independent tenRef order/partial failure/all close faults; productionPT0."""
import ast
import types
import unittest
from pg777_failure_full import REFERENCE,source


class Test(unittest.TestCase):
    def test_normal_and_each_acquisition_fault(self):
        def run(fault=None,inside=False):
            events=[]
            def event(name):
                events.append(name)
                if len(events)==fault:raise OSError('literal Ref fault')
            class Bus:
                def get_object(self,*a):return self
                def GetConnectionUnixProcessID(self,n):return 1
                def GetConnectionUnixUser(self,n):return 0
                def LoadUnit(self,u):event('load:'+u);return '/unit/'+u
                def RefUnit(self,u):event('ref:'+u)
                def GetUnit(self,u):event('get:'+u);return '/unit/'+u
                def UnrefUnit(self,u):event('unref:'+u)
                def close(self):event('close')
            env={'dbus':types.SimpleNamespace(SystemBus=lambda private:Bus(),Interface=lambda o,i:o)}
            node=next(n for n in ast.parse(REFERENCE).body if isinstance(n,ast.ClassDef));exec(compile(ast.Module(body=[node],type_ignores=[]),'<literal owned Ref>','exec'),env)
            try:
                with env['CaptureReferences']():
                    event('body')
                    if inside:raise ValueError('literal body fault')
                return events,None
            except (OSError,ValueError)as error:return events,error
        events,error=run();self.assertIsNone(error);self.assertEqual(42,len(events))
        self.assertEqual(10,sum(x.startswith('ref:')for x in events));self.assertEqual(10,sum(x.startswith('unref:')for x in events))
        refs=[x[4:]for x in events if x.startswith('ref:')];unrefs=[x[6:]for x in events if x.startswith('unref:')];self.assertEqual(refs[::-1],unrefs)
        for at in range(1,43):
            _,error=run(at)
            with self.subTest(at=at):self.assertIsInstance(error,OSError)
        _,error=run(inside=True);self.assertIsInstance(error,ValueError)
        ast.parse(source());self.assertIn('pg777-failure-full758-v1',source())


if __name__=='__main__':unittest.main()
