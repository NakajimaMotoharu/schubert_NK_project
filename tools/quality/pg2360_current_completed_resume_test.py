"""Literal independent admission/negative cases; no start or guest commands."""
import ast
import unittest
from pyflakes.api import check
from pg2358_current_completed_resume_observer import namespace,source
from pg2360_current_completed_resume_once import payload,RUN


class CurrentResume(unittest.TestCase):
    def test_whole_closure_and_reserved_start(self):
        files=namespace()['files']()
        self.assertEqual({'pg2358_watch_parent.py','pg457_stable_actor.py','pg462_observer_identity.py'},set(files))
        for n,s in files.items():self.assertEqual(0,check(s,'<actual observer '+n+'>'))
        self.assertIn('pg2356-current-runtime-verification-post-v1/manifest.safe.json',source())
        raw=payload({n:'a'*64 for n in files});tree=ast.parse(raw)
        self.assertIn("'originalBudgetSeconds':1800",raw)
        self.assertIn('>=12884901888',raw);self.assertIn('require(len(records)==10)',raw)
        self.assertIn('manager.UnrefUnit(u)',raw)
        self.assertLess(raw.index("persist('external-start-guard.private.json'"),raw.index("r=subprocess.run(['/usr/bin/systemctl','start'"))
        starts=[]
        for n in ast.walk(tree):
            if isinstance(n,ast.List):
                v=[getattr(x,'value',None)for x in n.elts]
                self.assertFalse(any(x in v for x in ['daemon-reload','stop','reset-failed','restart']))
                if 'start'in v:starts.append(v)
        self.assertEqual([['/usr/bin/systemctl','start','--no-block','schubert-nk-morning-controller.service']],starts)
        self.assertNotIn('0fd734',raw);self.assertNotIn('PG1846',raw)

    def test_fixed_run_argument_negative(self):
        raw=payload({});tree=ast.parse(raw)
        expr=next(n.args[0]for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='require'and 'declaration is not None and' in ast.get_source_segment(raw,n))
        code=compile(ast.Expression(expr),'<independent declaration negative>','eval')
        main='java dev.codex.schubert.nk.batch.file.MorningProcessMain'
        for d,expected in [(None,False),((0,main,False),False),((0,main+' --resume '+RUN,False),True),((0,main+' --resume foreign',False),False),((0,main+' --resume '+RUN+' extra',False),False)]:self.assertEqual(expected,eval(code,{'declaration':d}))


if __name__=='__main__':unittest.main()
