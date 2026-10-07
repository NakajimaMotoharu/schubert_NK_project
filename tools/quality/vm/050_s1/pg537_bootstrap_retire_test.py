"""Fresh caller peer separation, exact retirement protocol and no duplicate Unit action."""
import ast
import pathlib
import unittest


class RetireTest(unittest.TestCase):
    def test_new_artifact_version_does_not_rewrite_preserved_dependencies(self):
        wrapper=pathlib.Path(__file__).with_name('pg537_bootstrap_compile_v2.sh').read_text()
        cp=next(l for l in wrapper.splitlines()if l.startswith('task_cp='))
        expected=['pg498-pending-tools-v3','pg464-code-tools-v2','pg490-migration-tools-v4',
                  'pg481-pending-tools-v2','pg456-tools-v7']
        actual=[part.removeprefix('task_cp="').removeprefix('$task_work/')
                for part in cp.split(':')[:5]]
        self.assertEqual(expected,actual)
        self.assertIn('task_target=$task_work/pg537-bootstrap-tools-v2',wrapper)

    def test_actual_peer_query_and_missing_or_foreign_sessions(self):
        code=ast.parse(pathlib.Path(__file__).with_name('pg537_bootstrap_retire.py').read_text())
        node=next(n for n in ast.walk(code)if isinstance(n,ast.FunctionDef)and n.name=='connection')
        replies=[];queries=[]
        def command(args,limit):
            queries.append(args[-1]);self.assertEqual(4096,limit)
            return replies.pop(0)
        def require(v):
            if not v:raise ValueError('fixture refused')
        env={'backend':123,'live_database':True,'require':require,'env':{'command':command}}
        exec(compile(ast.Module(body=[node],type_ignores=[]),'<actual peer predicate>','exec'),env)
        replies.append(b'1\n0\n');env['connection'](False)
        self.assertIn("a.pid=123 and a.datname='schubert_nk'",queries[-1])
        self.assertIn("a.application_name='PG537-bootstrap-guard'",queries[-1])
        self.assertIn('objid=71419602',queries[-1])
        self.assertIn('pid not in(123,pg_backend_pid())',queries[-1])
        for bad in (b'0\n0\n',b'1\n1\n',b'2\n0\n',b'1\n',b'1\n0\n0\n'):
            replies.append(bad)
            with self.assertRaises(ValueError):env['connection'](False)
        env['live_database']=False;replies.append(b'0\n0\n');env['connection'](False)
        self.assertNotIn('application_name',queries[-1])
        replies.append(b'1\n0\n')
        with self.assertRaises(ValueError):env['connection'](False)
        for bad in (None,True,0,'False'):
            with self.assertRaises(ValueError):env['connection'](bad)

    def test_one_retirement_fresh_database_normal_close_precedes_release(self):
        here=pathlib.Path(__file__).parent
        java=(here/'Pg537BootstrapRetire.java').read_text()
        self.assertLess(java.index('refs.check("retire")'),java.index('RETIRE_DATABASE_SCOPE_CLOSE'))
        self.assertLess(java.index('RETIRE_DATABASE_SCOPE_CLOSE'),java.index('refs.release()'))
        self.assertNotIn('refs.check("run")',java)
        py=(here/'pg537_bootstrap_retire.py').read_text()
        self.assertLess(py.index("save('retire-reserved.private.json'"),py.index('retire_no_replace(credsfd'))
        self.assertIn('metadata(target)[:7]==prior[:7]',py)
        self.assertIn('os.fsync(credsfd);os.fsync(savefd)',py)
        self.assertIn("env['prepared'].clear()",py)
        self.assertIn('live_database=False',py)
        self.assertNotIn('systemctl',py)
        self.assertNotIn('pidfd_send_signal',py)


if __name__=='__main__':
    unittest.main()
