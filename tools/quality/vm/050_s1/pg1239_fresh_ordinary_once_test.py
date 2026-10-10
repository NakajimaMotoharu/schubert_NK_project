import ast
import unittest
import pg1239_fresh_ordinary_once as p

class FreshOnceTest(unittest.TestCase):
    def test_actual_watch_argv_literal_and_one_start_after_guard(self):
        s=p.payload();t=ast.parse(s);compile(s,'<actual one normal Root>','exec')
        n=next(n for n in t.body if isinstance(n,ast.FunctionDef)and n.name=='observer_argv')
        env={};exec(compile(ast.Module(body=[n],type_ignores=[]),'<actual independent-byte argv>','exec'),env)
        self.assertEqual(env['observer_argv']().split(b'\0'),[b'/usr/bin/python3',b'-B',b'/var/lib/pgpt-s1-preservation/pg1237-observer-v1/pg1237_watch_parent.py',b'd5b00104280028d9ea81b44c1d1c805f3c2861ed',b'0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d',b'PG1068',b''])
        starts=[]
        for n in ast.walk(t):
            if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=='run'and n.args and isinstance(n.args[0],ast.List):
                try:args=ast.literal_eval(n.args[0])
                except (ValueError,TypeError):continue
                if 'start'in args:starts.append(args)
        self.assertEqual(starts,[['/usr/bin/systemctl','start','--no-block','schubert-nk-morning-controller.service']])
        self.assertLess(s.index("persist('external-start-guard.private.json'"),s.index("result=subprocess.run(['/usr/bin/systemctl','start'"))
        self.assertTrue('snapshot()==frozen[\'native\']'in s)
        self.assertTrue('clientSuccessIsNotParentSuccess=True'in s)
        self.assertFalse("'sameActiveRunCutoffActivation':True"in s)

if __name__=='__main__':unittest.main()
