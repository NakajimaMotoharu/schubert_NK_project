import ast
import unittest
from pyflakes.api import check
import pg2446_question_current_observer as observer
import pg2448_question_current_noargs_once as once


class CurrentAdmission(unittest.TestCase):
    def test_whole_observer_bound_actual_boot_source_and_readonly(self):
        raw=observer.source();files=observer.namespace()['files']()
        for literal in ['b2d6f605-61cf-425f-8fbd-12d606f6ee66',
            'cdbc07cdf77370d521e64de8b327da7f6752139b',
            '6e069bc89f53b513c719c27fbe71167afbd07b48caa0a31c61bda3e2222f11cf',
            'pg2444-question-normal-publication-post-v1','PG2428']:self.assertIn(literal,raw)
        self.assertNotIn('3d69f5af',raw)
        self.assertEqual(set(files),{'pg2446_watch_parent.py','pg457_stable_actor.py','pg462_observer_identity.py'})
        self.assertNotIn('systemctl start',raw)
        for name,body in files.items():self.assertEqual(0,check(body,name))

    def test_whole_once_projected_independent_before_retains_native16(self):
        raw=once.payload({'pg2446_watch_parent.py':'a'*64})
        self.assertEqual(0,check(raw,'<complete admission>'))
        for literal in ['require(len(records)==16)','>=12884901888',
            'pg2448-question-current-noargs-once-v1','pg2446-observer-v1',
            'cdbc07cdf77370d521e64de8b327da7f6752139b',
            '6e069bc89f53b513c719c27fbe71167afbd07b48caa0a31c61bda3e2222f11cf',
            "'--resume'not in declaration[1]","require(watch==observer()and native==snapshot())"]:
            self.assertIn(literal,raw)
        self.assertEqual(1,raw.count("['/usr/bin/systemctl','start','--no-block','schubert-nk-morning-controller.service']"))
        self.assertNotIn('require(len(records)==38)',raw)
        self.assertNotIn('daemon-reload',raw)
        tree=ast.parse(raw)
        scopes=[n for n in tree.body if isinstance(n,ast.Try)and any(isinstance(x,ast.FunctionDef)and x.name=='snapshot'for x in n.body)]
        self.assertEqual(1,len(scopes))
        self.assertTrue(any(isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=='run'for n in ast.walk(scopes[0])))


if __name__=='__main__':unittest.main()
