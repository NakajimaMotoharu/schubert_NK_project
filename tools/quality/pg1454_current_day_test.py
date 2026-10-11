import ast
import unittest
from pg1454_current_day_observer import source,namespace
from pg1455_current_day_before import payload


class CurrentDayTest(unittest.TestCase):
    def test_actual_observer_boot_and_owner_binding(self):
        env=namespace();watch=env['watch']();compile(watch,'<actual watch>','exec')
        self.assertIn("BOOT='3d69f5af-6bac-46b1-a540-7591c4a79a0d'",watch)
        self.assertIn("deadline=int(m['ExecMainStartTimestampMonotonic'])/1e6+1860",watch)
        self.assertIn('same(roots[role],aa)',watch)
        self.assertEqual({'pg1454_watch_parent.py','pg457_stable_actor.py','pg462_observer_identity.py'},set(env['files']()))
        self.assertIn('pg1453-current-cold-independent-post-v1/manifest.safe.json',source())
        calls=[ast.unparse(n.func)for n in ast.walk(ast.parse(watch))if isinstance(n,ast.Call)]
        self.assertNotIn('os.kill',calls)
        self.assertNotIn('--resume',watch)

    def test_full_independent_before_and_actual_day(self):
        s=payload();compile(s,'<whole before>','exec')
        self.assertIn("require(len(same_day)==0)",s)
        self.assertIn("datetime.timezone(datetime.timedelta(hours=9))",s)
        self.assertIn('first==before[\'current\']',s)
        self.assertIn('operatorInvalidIssued=False',s)
        self.assertNotIn('StartupPermitFiles',s)


if __name__=='__main__':unittest.main()
