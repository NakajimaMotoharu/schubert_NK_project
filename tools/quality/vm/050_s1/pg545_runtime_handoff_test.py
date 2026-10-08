"""Independent owner/null/type/task membership and one-pair ordering, management only."""
import ast
import copy
from pathlib import Path
import unittest
from pg543_retirement_contract import old_peer_state


class FixedOwner(unittest.TestCase):
    def test_peer_expiry_is_not_normal_close(self):
        self.assertEqual(old_peer_state([b'1',b'1',b'0',b'1'],False,True),'OWNED_UNKNOWN')
        for finished in (False,True):self.assertEqual(old_peer_state([b'0']*4,finished,True),'EXPIRED_UNKNOWN')
        for good in ([b'0']*4,[b'1',b'1',b'0',b'1']):
            for index in range(4):
                for badvalue in (None,0,b'2',b'foreign'):
                    bad=good.copy();bad[index]=badvalue
                    with self.assertRaises(ValueError):old_peer_state(bad,False,True)
        with self.assertRaises(ValueError):old_peer_state([b'0']*4,False,False)
        with self.assertRaises(ValueError):old_peer_state([b'1',b'0',b'0',b'0'],False,True)
        with self.assertRaises(ValueError):old_peer_state([b'1',b'1',b'0',b'1'],True,True)
    def test_identity(self):
        text=(Path(__file__).parent/'pg545_runtime_owned_handoff_v1.py').read_text()
        node=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)and n.name=='identity')
        env={};exec(compile(ast.Module(body=[node],type_ignores=[]),'<independent literal owner>','exec'),env)
        good={'pid':42,'ticks':123,'parent':7,'argv':'fixed','uid':['0']*4,'children':{43}}
        self.assertTrue(env['identity'](good,42,123,'fixed',7))
        for key in good:
            for action in ('missing','null','foreign'):
                bad=copy.deepcopy(good)
                if action=='missing':del bad[key]
                else:bad[key]=None if action=='null'else'foreign'
                self.assertFalse(env['identity'](bad,42,123,'fixed',7))
        for key,value in (('pid',True),('ticks',True),('parent',True),('children',{True}),('children',{None}),('uid',['0','0','1','0'])):
            self.assertFalse(env['identity']({**good,key:value},42,123,'fixed',7))
        self.assertFalse(env['identity']({**good,'extra':1},42,123,'fixed',7))

    def test_order_and_exact_generation(self):
        s=(Path(__file__).parent/'pg545_runtime_owned_handoff_v1.py').read_text()
        self.assertIn('PID=573159',s);self.assertIn('CHILD=573188',s)
        self.assertIn('/pg545-runtime-owned-handoff-v1',s)
        self.assertNotIn('pg536-',s)
        self.assertEqual(s.count('signal.pidfd_send_signal('),2)
        self.assertLess(s.index("save('term-reserved.private.json'"),s.index('signal.pidfd_send_signal(childfd'))
        self.assertLess(s.index('wait_gone(CHILD)'),s.index('signal.pidfd_send_signal(parentfd'))
        self.assertIn("phase='NONE';owner();peer(env);require(before==snapshot() and before==snapshot())",s)
        self.assertNotIn('systemctl',s);self.assertNotIn('unlink(',s)
        self.assertIn('allNewReferencesNormallyClosed',s);self.assertIn('oldCloseUNKNOWN',s)
        wrapper=(Path(__file__).parent/'pg545_runtime_handoff_native_v1.py').read_text()
        self.assertIn("RUN='PG545-runtime-'+mode+'-v1'",wrapper)
        self.assertNotIn('PG545-bootstrap',wrapper)
        self.assertIn('exec(compile(',wrapper)


if __name__=='__main__':unittest.main()
