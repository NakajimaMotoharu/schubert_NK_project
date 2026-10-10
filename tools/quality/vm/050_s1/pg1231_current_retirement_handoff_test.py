import ast
import json
from pathlib import Path
import tempfile
import unittest
import pg1231_current_retirement_handoff as p

class HandoffTest(unittest.TestCase):
    def test_actual_once_callbacks_writer_and_readonly_post_contract(self):
        s=p.payload();t=ast.parse(s);compile(s,'<actual fixed handoff>','exec')
        node=next(n for n in t.body if isinstance(n,ast.Assign)and any(isinstance(x,ast.Name)and x.id=='WRITER_SOURCE'for x in n.targets))
        env={};exec(ast.literal_eval(node.value),env)
        with tempfile.TemporaryDirectory(prefix='pg1231-durable-')as tmp:
            root=Path(tmp);vector=b'{"source":"independent","oldNormalClose":false}'
            env['save'](root,'after.private.json',vector)
            self.assertEqual((root/'after.private.json').read_bytes(),vector)
            self.assertEqual((root/'after.private.json').stat().st_mode&0o777,0o600)
            with self.assertRaises(FileExistsError):env['save'](root,'after.private.json',vector)
        # Exercise actual extracted once algorithm, including generation change;
        # no OS process or VM mutation occurs in this host callback fixture.
        fun=next(n for n in t.body if isinstance(n,ast.FunctionDef)and n.name=='terminate_once')
        scope={};exec(compile(ast.Module(body=[fun],type_ignores=[]),'<actual once function>','exec'),scope)
        actions=[];same=lambda pid,ticks:{'pid':pid,'ticks':ticks}
        scope['terminate_once'](7,8,same,lambda *v:actions.append('reserve'),lambda pid:11,lambda fd:actions.append('send'),lambda fd:True,lambda fd:actions.append('close'))
        self.assertEqual(actions,['reserve','send','close'])
        seq=iter([{'generation':1},{'generation':2}]);actions=[]
        with self.assertRaises(ValueError):scope['terminate_once'](7,8,lambda *v:next(seq),lambda *v:actions.append('reserve'),lambda pid:11,lambda fd:actions.append('send'),lambda fd:True,lambda fd:actions.append('close'))
        self.assertEqual(actions,['close'])
        self.assertTrue("lines[-2:]==[b'0',b'0']"in s)
        self.assertTrue('signals==2'in s)
        self.assertFalse('json.dump('in s)
        self.assertEqual(s.count('terminate_once(560266,'),1);self.assertEqual(s.count('terminate_once(560237,'),1)

if __name__=='__main__':unittest.main()
