import unittest
import pg1237_fresh_day_observer as p

class FreshObserverTest(unittest.TestCase):
    def test_actual_watch_source_same_generation_and_parent_start_bound(self):
        env={'__file__':p.__file__,'__name__':'qualified_new_day_observer'};s=p.source();exec(compile(s,'<actual fresh watch namespace>','exec'),env)
        watch=env['watch']();compile(watch,'<actual current watch>','exec')
        self.assertTrue('pg1236-completed-runtime-retired-post-v1.safe.json'in s)
        self.assertTrue("deadline=int(m['ExecMainStartTimestampMonotonic'])/1e6+1860"in watch)
        self.assertTrue('same(roots[role],aa)'in watch)
        self.assertFalse('--resume'in watch)
        self.assertFalse("'start'"in watch);self.assertFalse("'stop'"in watch)
        for name,code in env['files']().items():compile(code,'<actual '+name+'>','exec')
        self.assertEqual(set(env['files']()),{'pg1237_watch_parent.py','pg457_stable_actor.py','pg462_observer_identity.py'})

if __name__=='__main__':unittest.main()
