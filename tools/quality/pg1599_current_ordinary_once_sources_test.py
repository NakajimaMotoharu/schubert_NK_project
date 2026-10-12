"""Execute AST ownership/scope oracle against actual full start payload."""
import ast
import unittest
from pg1599_current_ordinary_once_sources_v2 import payload

class RefLifetimeTest(unittest.TestCase):
    def test_all_snapshot_calls_within_same_ref_try_and_stop_after_normal_close(self):
        raw=payload({'pg1597_watch_parent.py':'a'*64,'pg457_stable_actor.py':'b'*64,'pg462_observer_identity.py':'c'*64});tree=ast.parse(raw)
        held=next(n for n in tree.body if isinstance(n,ast.Try)and any(isinstance(x,ast.FunctionDef)and x.name=='snapshot'for x in n.body))
        final=min(n.lineno for n in held.finalbody)
        calls=[n for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='snapshot']
        self.assertGreaterEqual(len(calls),3)
        self.assertTrue(all(held.lineno<n.lineno<final for n in calls))
        start=raw.index("subprocess.run(['/usr/bin/systemctl','start','--no-block','schubert-nk-morning-controller.service']")
        self.assertLess(raw.index("persist('external-start-guard.private.json'"),start)
        self.assertLess(start,raw.index('manager.UnrefUnit(u)'))
        self.assertLess(raw.index('bus.close()'),raw.index('print(json.dumps(current))'))
        self.assertEqual(raw.count('manager.UnrefUnit(u)'),1)
        self.assertEqual(raw.count("['/usr/bin/systemctl','start','--no-block','schubert-nk-morning-controller.service']"),1)
        self.assertIn('pg1600-current-ordinary-once-v2',raw)
        self.assertNotIn('pg1598-current-ordinary-once-v1',raw)

if __name__=='__main__':unittest.main()
