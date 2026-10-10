import ast
import tempfile
import unittest
import pathlib
from pg1252_fresh_stop_fixed_handoff import payload

class FixedFreshOnceHandoffTest(unittest.TestCase):
    def test_actual_once_callback_generation_change_and_durable_writer(self):
        s=payload();t=ast.parse(s);compile(s,'<actual complete handoff>','exec')
        n=next(n for n in t.body if isinstance(n,ast.FunctionDef)and n.name=='terminate_once')
        env={};exec(compile(ast.Module(body=[n],type_ignores=[]),'<actual once callback>','exec'),env)
        events=[]
        def verify(pid,ticks):events.append('verify');return {'fixed':True}
        env['terminate_once'](691104,6303259,verify,lambda p,v:events.append('reserve'),lambda p:9,lambda fd:events.append('signal'),lambda fd:True,lambda fd:events.append('close'))
        self.assertEqual(events,['verify','verify','reserve','verify','signal','close'])
        values=iter([{'fixed':True},{'fixed':False}]);events=[]
        with self.assertRaises(ValueError):env['terminate_once'](691104,6303259,lambda p,t:next(values),lambda p,v:None,lambda p:9,lambda fd:events.append('signal'),lambda fd:True,lambda fd:events.append('close'))
        self.assertEqual(events,['close'])
        source=next(n.value.value for n in t.body if isinstance(n,ast.Assign)and any(isinstance(x,ast.Name)and x.id=='WRITER'for x in n.targets))
        writer={};exec(compile(source,'<actual durable bytes writer>','exec'),writer)
        with tempfile.TemporaryDirectory()as d:
            p=pathlib.Path(d);writer['save'](p,'proof.private',b'fixed bytes');self.assertEqual((p/'proof.private').read_bytes(),b'fixed bytes')
            with self.assertRaises(FileExistsError):writer['save'](p,'proof.private',b'changed')

if __name__=='__main__':unittest.main()
