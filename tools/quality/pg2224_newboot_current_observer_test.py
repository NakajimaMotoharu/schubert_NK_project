import unittest
from pg2224_newboot_current_observer import source,namespace


class NewBootObserver(unittest.TestCase):
    def test_whole_stage_watch_and_three_file_closure(self):
        s=source();n=namespace();f=n['files']()
        self.assertEqual(set(f),{'pg2224_watch_parent.py','pg457_stable_actor.py','pg462_observer_identity.py'})
        for value in ['pg2218-current-newboot-cold-independent-post-v1/manifest.safe.json',
          'b2d6f605-61cf-425f-8fbd-12d606f6ee66','PG2126','62213f357c9dab3b00b557549426b091a03ace6557a62f4410999a02028a332c','3b7f3567b54f91f3a9dbeb859e8dd77e8353a2c8']:
            self.assertIn(value,s)
        watch=f['pg2224_watch_parent.py']
        self.assertIn("BOOT='b2d6f605-61cf-425f-8fbd-12d606f6ee66'",watch)
        self.assertIn('deadline=int(m[\'ExecMainStartTimestampMonotonic\'])/1e6+1860',watch)
        self.assertNotIn('PG1292',s+watch)
        self.assertNotIn('3d69f5af',watch)
        for x in f.values():compile(x,'<actual immutable closure>','exec')


if __name__=='__main__':unittest.main()
