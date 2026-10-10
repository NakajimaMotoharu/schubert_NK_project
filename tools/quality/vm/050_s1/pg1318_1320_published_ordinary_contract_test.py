"""Complete actual observer/before/start composition; independent noargs/skip contracts."""
import unittest
from pg1318_published_source_observer import source
from pg1319_published_source_ordinary_before import payload
from pg1320_published_source_ordinary_once import compose


class PublishedOrdinaryTest(unittest.TestCase):
    def test_actual_observer_current_source_generation_and_budget(self):
        env={'__file__':__file__,'__name__':'fixture'}
        code=source();exec(compile(code,'<actual current observer>','exec'),env)
        self.assertIn('pg1315-ordinary-publication-independent-v1.safe.json',code)
        self.assertNotIn('PG1068',code)
        # __file__ parent intentionally uses the same tool directory.
        watch=env['watch']();compile(watch,'<actual watch>','exec')
        self.assertIn("sys.argv[3]=='PG1292'",watch)
        self.assertIn('same(roots[role],aa)',watch)
        self.assertIn("deadline=int(m['ExecMainStartTimestampMonotonic'])/1e6+1860",watch)
        self.assertNotIn("'start'",watch);self.assertNotIn("'stop'",watch)

    def test_actual_before_accepts_legal_same_day_without_row_edits(self):
        code=payload();compile(code,'<actual full before>','exec')
        self.assertIn('existingSuccessfulInspectorStepsForDate=len(same_day)',code)
        self.assertNotIn('require(not same_day)',code)
        self.assertIn("'--resume'not in argv",code)
        self.assertIn('requiredGuestWriteAndCloseBytes=805306368',code)
        self.assertNotIn('delete from',code.lower())
        self.assertNotIn('update schubert',code.lower())

    def test_actual_start_closed_input_one_command_and_original_budget(self):
        hashes={n:'a'*64 for n in ['pg1318_watch_parent.py','pg457_stable_actor.py','pg462_observer_identity.py']}
        code=compose('b'*64,hashes);compile(code,'<complete one normal Root>','exec')
        self.assertEqual(code.count("'/usr/bin/systemctl','start','--no-block','schubert-nk-morning-controller.service'"),1)
        self.assertLess(code.index("persist('external-start-guard.private.json'"),code.index("'/usr/bin/systemctl','start'"))
        self.assertIn('frozen[\'current\']==pub_after',code)
        self.assertIn('originalBudgetSeconds\':1800',code)
        self.assertIn('existingSuccessfulInspectorStepsForDate\'])is int',code)
        self.assertNotIn('require(not same_day)',code)
        self.assertNotIn('d5b00104280028d9ea81b44c1d1c805f3c2861ed',code)
        for before,values in [(None,hashes),('b'*63,hashes),('g'*64,hashes),('b'*64,None),('b'*64,{}),('b'*64,dict(hashes,foreign='a'*64))]:
            with self.assertRaises(ValueError):compose(before,values)


if __name__=='__main__':unittest.main()
