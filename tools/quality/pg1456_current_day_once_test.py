import ast
import unittest
from pg1456_current_day_once import compose


class OnceTest(unittest.TestCase):
    def test_single_normal_dispatch_after_durable_guard(self):
        names={'pg1454_watch_parent.py':'b'*64,'pg457_stable_actor.py':'c'*64,'pg462_observer_identity.py':'d'*64}
        s=compose('a'*64,names);compile(s,'<once>','exec')
        self.assertEqual(1,s.count("'start','--no-block','schubert-nk-morning-controller.service'"))
        self.assertLess(s.index("persist('external-start-guard.private.json'"),s.index("'start','--no-block'"))
        self.assertIn('ordinaryNoargs',s);self.assertIn('originalBudgetSeconds\':1800',s)
        self.assertIn('watch_identity()==watch',s)
        self.assertNotIn('StartupPermitFiles',s)
        self.assertNotIn("'stop'",s)
        self.assertNotIn('SIGKILL',[n.attr for n in ast.walk(ast.parse(s))if isinstance(n,ast.Attribute)])

    def test_missing_unknown_null_hash_rejected(self):
        names={'pg1454_watch_parent.py':'b'*64,'pg457_stable_actor.py':'c'*64,'pg462_observer_identity.py':'d'*64}
        for invalid in [None,'', 'A'*64,'a'*63]:
            with self.assertRaises(ValueError):compose(invalid,names)
        bad=dict(names);bad['pg1454_watch_parent.py']=None
        for invalid in [None,[],{},dict(names,extra='e'*64),bad]:
            with self.assertRaises(ValueError):compose('a'*64,invalid)


if __name__=='__main__':unittest.main()
