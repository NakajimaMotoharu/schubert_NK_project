import unittest
import pg2176_newsource_normal_observer as p


class Observer(unittest.TestCase):
    def test_actual_newsource_readonly_files(self):
        raw=p.source();ns=p.namespace();files=ns['files']()
        self.assertIn('pg2174-normal-publication-full-post-v1',raw)
        self.assertIn('3b7f3567b54f91f3a9dbeb859e8dd77e8353a2c8',raw)
        self.assertIn('62213f357c9dab3b00b557549426b091a03ace6557a62f4410999a02028a332c',raw)
        self.assertEqual(set(files),{'pg2176_watch_parent.py','pg457_stable_actor.py','pg462_observer_identity.py'})
        self.assertIn('PG2126',files['pg2176_watch_parent.py'])
        self.assertNotIn('systemctl start',raw)


if __name__=='__main__':unittest.main()
