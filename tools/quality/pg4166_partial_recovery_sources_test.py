import ast
import unittest
from pyflakes.api import check
import pg4166_partial_recovery_sources as p


class PartialTest(unittest.TestCase):
    def test_complete_closure_and_no_old_source_or_wrong_oracle_replay(self):
        for text in [p.controller(),p.post()]:
            self.assertEqual(0,check(text,'<new partial>'))
            self.assertFalse('config()==fixed_config'in text)
            self.assertTrue('same_configurations'in text)
        raw=p.controller();self.assertTrue('prior-terminal-observed.private'in raw)
        self.assertTrue("'newStopCount':5 if MODE=='recover'else 0"in raw)
        self.assertTrue("'old4152Normal':False"in raw)
        self.assertTrue("'frames':[{'file':Path(t.filename).name,'line':t.lineno,'function':t.name}"in raw)

    def test_actual_caddy_callback_only_authenticates_prior_terminal_no_send(self):
        raw=p.controller();node=next(n for n in ast.walk(ast.parse(raw))if isinstance(n,ast.FunctionDef)and n.name=='stop')
        calls=[]
        def require(v):
            if not v:raise ValueError('fixture')
        class Path:
            def exists(self):return False
        class Terminal:
            def normal_terminal(self,b,a):calls.append('normal');return True
            def kernel_empty(self,u):calls.append('kernel')
        ns={'require':require,'terminal_contract':Terminal(),'captures':{'caddy.service':'historical'},
          'show_terminal':lambda unit:'actual','Path':lambda unused:Path(),'holder':lambda:calls.append('owner')}
        exec(compile(ast.Module(body=[node],type_ignores=[]),'<actual callback>','exec'),ns)
        ns['stop']('caddy.service');self.assertEqual(['normal','kernel','owner'],calls)

    def test_new_namespaces_and_fresh_before_oracles_preserved(self):
        a,b=p.controller(),p.post()
        self.assertTrue("save=base/('pg4184-partial-owned-recovery-v1-'+MODE)"in a)
        self.assertTrue("RECOVERY='/var/lib/pgpt-s1-preservation/pg4184-partial-owned-recovery-v1-recover'"in b)
        self.assertTrue("before['database']['rows']"in b)
        self.assertFalse("before['actors']==reference['actors']"in b)


if __name__=='__main__':unittest.main()
