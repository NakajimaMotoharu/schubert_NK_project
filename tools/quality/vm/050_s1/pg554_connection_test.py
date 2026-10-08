"""PT-OPS-PG554-CON001: source/dependency and one-shot start ordering, no live operations."""
import ast
from pathlib import Path
import unittest
from pg554_stable_actor import ENTRIES
from pg553_precondition import SOURCE,DIGEST

R=Path(__file__).resolve().parent


class Test(unittest.TestCase):
    def test_current_source_and_whole_role_binding(self):
        watch=(R/'pg554_watch_parent.py').read_text();shell=(R/'pg554_parent_observer_v1.sh').read_text()
        self.assertIn(SOURCE,shell);self.assertIn(DIGEST,shell);self.assertIn(' PG548',shell)
        self.assertIn("sys.argv[3]=='PG548'",watch)
        self.assertIn('pg554_stable_actor',watch);self.assertIn('pg462_observer_identity',watch)
        self.assertNotIn('PG495',watch+shell)
        self.assertIn('dev.codex.schubert.nk.api.maintenance.InspectorLauncher',ENTRIES)
        self.assertIn('dev.codex.schubert.nk.batch.file.CleanupProcessMain',ENTRIES)
        tree=ast.parse(watch)
        units=next(n.value for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='UNITS'for t in n.targets))
        self.assertEqual(set(ast.literal_eval(units)),{'morning','api','web','caddy','cleanup','inspector','expiry','backup'})
        self.assertIn('wholeMorningAccepted',watch);self.assertIn('int(m[\'ExecMainStartTimestampMonotonic\'])/1e6+1860',watch)

    def test_durable_reservation_precedes_only_parent_start(self):
        tree=ast.parse((R/'pg554_external_start_once.py').read_text())
        payload=next(ast.literal_eval(n.value)for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='payload'for t in n.targets))
        self.assertEqual(payload.count("['/usr/bin/systemctl','start','--no-block','schubert-nk-morning-controller.service']"),1)
        self.assertLess(payload.index("persist('external-start-guard.private.json'"),payload.index("['/usr/bin/systemctl','start'"))
        self.assertLess(payload.index("shutil.copytree"),payload.index("persist('external-start-guard.private.json'"))
        self.assertIn('os.O_EXCL',payload);self.assertIn('os.fsync',payload)
        self.assertIn("'--resume' not in execstart",payload)
        self.assertIn("m.stopped()==before['units']",payload)
        self.assertIn('originalBudgetSeconds',payload);self.assertIn('repeatForbidden',payload)
        self.assertNotIn('systemctl stop',payload)


if __name__=='__main__':unittest.main()
