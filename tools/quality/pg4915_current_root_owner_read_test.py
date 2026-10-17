import ast
import unittest
from pyflakes.api import check,checkPath
import pg4915_current_root_owner_read as role


class Owner(unittest.TestCase):
    def test_same_actual_generation_strict_every_field_and_no_control_action(self):
        b={'job':'literal-job','invocation':'literal-inv','start':123}
        state={'MainPID':'456','ControlPID':'0','Job':'literal-job','InvocationID':'literal-inv','ExecMainStartTimestampMonotonic':'123','ActiveState':'activating','SubState':'start'}
        role.validate(state,b,456)
        for key in state:
            with self.subTest(key=key),self.assertRaises(ValueError):role.validate({**state,key:'foreign'},b,456)
        raw=role.payload();self.assertEqual(0,check(raw,'<current pidfd Root read>'))
        calls=[n for n in ast.walk(ast.parse(raw)) if isinstance(n,ast.Call) and ast.unparse(n.func)=='subprocess.run']
        self.assertEqual(1,len(calls));self.assertIn("'systemctl','show'",raw)
        for text in ('os.pidfd_open','poll.poll(0)==[]',"'rootGenuineDone':False","'stateChangingActions':0"):
            self.assertIn(text,raw)
        self.assertEqual(0,checkPath(role.__file__));self.assertEqual(0,checkPath(__file__))


if __name__=='__main__':unittest.main()
