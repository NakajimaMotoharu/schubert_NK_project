"""Independent finite admission, one-use reservation, observer-before-start source binding."""
import ast
from pathlib import Path
import unittest

R=Path(__file__).resolve().parent


def literal(name):
    module=ast.parse((R/'pg637_resume_once.py').read_text())
    return ast.literal_eval(next(n.value for n in module.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id==name for t in n.targets)))


class Binding(unittest.TestCase):
    def test_same_run_finite_seal_no_ordinary_newrun(self):
        self.assertEqual(literal('SOURCE'),'36fe7a0b938489d61d17d49c1c30a6fbbef699d5')
        self.assertEqual(literal('DIGEST'),'57a5355d7d0c6a3af7ff2ec619eacee20ee9236916de25e02b95953ffa6aa2fe')
        payload=literal('PAYLOAD');compile(payload,'<independentadmission>','exec')
        for v in ('c946eaae7147aff0fb328bfabda0d779133f7c04cc30a9a0427d58ae7da76d2e',
                  'pg635-resume-preparation-v1','==494','==19','pg635-once-resume.conf',
                  "expected['parentPid1']",'datetime.timedelta(minutes=2)',"'originalBudgetSeconds':1800"):
            self.assertIn(v,payload)
        start=payload.index("persist('external-start-guard.private.json'")
        self.assertLess(start,payload.index("subprocess.run(['/usr/bin/systemctl','start','--no-block'"))
        self.assertEqual(payload.count("subprocess.run(['/usr/bin/systemctl','start'"),1)
        self.assertIn("not os.path.lexists(root/'external-start-guard.private.json')",payload)
        self.assertIn("'e49243d5-de84-4714-8612-6912ddc17e9e'",payload)
        self.assertNotIn('daemon-reload',payload);self.assertNotIn('reset-failed',payload)
        outer=(R/'pg637_resume_once.py').read_text();self.assertIn("(W/'pg638-observer-v1.started').exists()",outer)
        self.assertIn("not(W/'pg638-observer-v1.exit').exists()",outer)
        self.assertIn("'observerPrepared':True,'source':SOURCE,'manifestSha256':DIGEST,'starts0':True",outer)

    def test_observer_current_source_and_original_budget_only(self):
        watcher=(R/'pg638_watch_parent.py').read_text();wrapper=(R/'pg638_observer.py').read_text()
        self.assertIn("sys.argv[3]=='PG631'",watcher);self.assertNotIn('PG621',watcher)
        self.assertIn("'schema':'028'",watcher);self.assertIn('same(roots[role],aa)',watcher)
        self.assertIn("'wholeMorningAccepted':False",watcher)
        self.assertIn("pg637-fresh-resume-v2/before.private.json",wrapper)
        self.assertIn("W/'pg637-prepare-v2.exit'",wrapper)
        self.assertIn("'pg638_watch_parent.py'",wrapper)
        for text in (watcher,wrapper):
            self.assertNotIn('systemctl start',text);self.assertNotIn('systemctl stop',text)

    def test_ref_owned_admission_and_start_scope(self):
        tree=ast.parse(literal('PAYLOAD'))
        guarded=next(n for n in tree.body if isinstance(n,ast.Try) and n.finalbody)
        source=ast.unparse(guarded)
        self.assertIn('manager.RefUnit(unit)',source)
        self.assertIn('manager.UnrefUnit(unit)',source)
        self.assertIn('bus.close()',source)
        self.assertLess(source.index('manager.RefUnit(unit)'),source.index("MODE == 'prepare'"))
        self.assertGreater(source.index('finally:'),source.index("'external-start-issued.private.json'"))
        self.assertIn('dbus.SystemBus(private=True)',literal('PAYLOAD'))


if __name__=='__main__':unittest.main()
