"""Independent once/budget/completed-run contract and actual composed scope closure."""
import ast
import unittest
from pg2015_completed_run_fresh_resume_once import payload,RUN


class Resume(unittest.TestCase):
    def test_actual_start_inside_ten_refs_native26_and_closed_run(self):
        raw=payload({'pg2010_watch_parent.py':'a'*64,'pg457_stable_actor.py':'b'*64,'pg462_observer_identity.py':'c'*64})
        tree=ast.parse(raw)
        scope=next(n for n in tree.body if isinstance(n,ast.Try)and any(isinstance(x,ast.FunctionDef)and x.name=='snapshot'for x in n.body))
        starts=[]
        for n in ast.walk(scope):
            if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=='run'and n.args and isinstance(n.args[0],ast.List):
                values=[getattr(x,'value',None)for x in n.args[0].elts]
                if 'start'in values:starts.append(values)
        self.assertEqual([['/usr/bin/systemctl','start','--no-block','schubert-nk-morning-controller.service']],starts)
        self.assertTrue("require(len(records)==26)"in raw)
        self.assertTrue("'originalBudgetSeconds':1800"in raw)
        self.assertTrue('>=12884901888'in raw)
        self.assertTrue("'selectedRun':'"+RUN+"'"in raw)
        self.assertTrue('manager.UnrefUnit(u)'in ast.get_source_segment(raw,scope))
        for n in ast.walk(tree):
            if isinstance(n,ast.List):
                values=[getattr(x,'value',None)for x in n.elts]
                self.assertFalse(any(v in values for v in ['daemon-reload','reset-failed','prepare-resume','stop']), 'no repeated command mutation')
        self.assertLess(raw.index("persist('external-start-guard.private.json'"),raw.index("r=subprocess.run(['/usr/bin/systemctl','start'"))

    def test_actual_argv_condition_rejects_old_or_foreign_run(self):
        raw=payload({});target=next(n for n in ast.walk(ast.parse(raw))if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='require'and 'declaration is not None and' in ast.get_source_segment(raw,n))
        code=compile(ast.Expression(target.args[0]),'<actual fixed argv condition>','eval')
        main='java dev.codex.schubert.nk.batch.file.MorningProcessMain'
        for value,wanted in [(None,False),((0,main,False),False),((0,main+' --resume '+RUN,False),True),((0,main+' --resume foreign',False),False)]:
            self.assertEqual(wanted,eval(code,{'declaration':value}))


if __name__=='__main__':unittest.main()
