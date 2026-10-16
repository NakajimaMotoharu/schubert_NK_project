import ast
import unittest
from pyflakes.api import check
import pg4220_same_peer_current_observer as p


class ObserverTest(unittest.TestCase):
    def test_all_oracles_and_original_poll_budget_remain_exact(self):
        old=p.previous.namespace()['files']()['pg4012_watch_parent.py'];new=p.watch()
        before={n.name:ast.dump(n)for n in ast.parse(old).body if isinstance(n,ast.FunctionDef)}
        after={n.name:ast.dump(n)for n in ast.parse(new).body if isinstance(n,ast.FunctionDef)}
        self.assertEqual(set(before),set(after))
        self.assertTrue(all(before[k]==after[k]for k in before if k!='manager'))
        loop_old=next(n for n in ast.parse(old).body if isinstance(n,ast.While))
        loop_new=next(n for n in ast.walk(ast.parse(new))if isinstance(n,ast.While))
        self.assertEqual(ast.dump(loop_old),ast.dump(loop_new))
        self.assertTrue("reader.RefUnit(unit);held.append(unit)"in new)
        self.assertTrue("reversed(held):reader.UnrefUnit(unit)"in new)

    def test_complete_four_artifact_namespace_and_static_closure(self):
        ns=p.namespace();files=ns['files']()
        self.assertEqual({'pg4220_watch_parent.py','pg457_stable_actor.py','pg462_observer_identity.py','pg4216_same_peer_observer_manager.py'},set(files))
        for name,raw in files.items():
            with self.subTest(name=name):self.assertEqual(0,check(raw,'<'+name+'>'))
        self.assertTrue('pg4220' in p.source())
        self.assertNotIn('pg4012',p.source())


if __name__=='__main__':unittest.main()
