"""Independent caller/peer grammar and source no-repeat-action management oracle."""
import ast
from pathlib import Path
import re
import unittest


class PostReadback(unittest.TestCase):
    def test_no_repeat_namespace_or_unit_action(self):
        root=Path(__file__).parent
        java=(root/'Pg546PostRetirementAdmission.java').read_text()
        python=(root/'pg546_post_retirement_refs.py').read_text()
        for text in(java,python):
            for marker in('unlinkEntry(','.unlink(','.rename(','"daemon-reload"','"--no-block"','"systemctl","start"'):
                self.assertNotIn(marker,text)
        self.assertIn('args!=null',java)
        self.assertIn('directory.atDirectory(',java)
        self.assertLess(java.index('db.rollback();db.close();'),java.index('refs.release();'))
        self.assertIn("load(owner,post=True,caddy_before=boundary['caddyExecStartPre'])",python)
        self.assertIn("save('after.private.json',snapshot())",python)
        self.assertLess(python.index("if action=='release':live=False"),python.index('manager.UnrefUnit('))
        wrapper=(root/'pg546_post_native_v1.py').read_text()
        self.assertIn("sys.argv[1] in ('stage','readback')",wrapper)
        self.assertIn("'run':'PG546-'+mode+'-v1'",wrapper)
        self.assertNotIn('pg543-verify-',wrapper)

    def test_live_and_closed_peer_queries_are_fixed(self):
        text=(Path(__file__).parent/'pg546_post_retirement_refs.py').read_text()
        node=next(n for n in ast.walk(ast.parse(text))if isinstance(n,ast.FunctionDef)and n.name=='connection')
        seen=[]
        def require(v):self.assertTrue(v)
        def command(args,limit):
            self.assertEqual(args[:9],['/usr/bin/sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1'])
            self.assertEqual(limit,4096)
            sql=args[-1];self.assertIn('a.pid=123 and ',sql);self.assertIsNone(re.search(r'[0-9]and\b',sql))
            self.assertIn('pid not in(123,pg_backend_pid())',sql)
            self.assertIn('objsubid=1 and granted',sql)
            seen.append(sql);return b'1\n0\n1\n'if env['live']else b'0\n0\n0\n'
        env={'backend':123,'live':True,'require':require,'env':{'command':command}}
        exec(compile(ast.Module(body=[node],type_ignores=[]),'<independent peer grammar>','exec'),env)
        env['connection']();self.assertIn("a.application_name='PG546-post-retirement-readback'",seen[-1]);self.assertIn("mode='ExclusiveLock'",seen[-1])
        env['live']=False;env['connection']();self.assertNotIn("a.application_name=",seen[-1])


if __name__=='__main__':unittest.main()
