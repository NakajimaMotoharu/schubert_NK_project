"""Same transport/actor oracle, new source/namespace, no historical session authority."""
import unittest
from pyflakes.api import check,checkPath
import pg4734_new_current_same_peer_observer as observer


class SamePeer(unittest.TestCase):
    def test_closed_four_files_and_exact_new_current_source_bom(self):
        files=observer.files();ns=observer.namespace()
        self.assertEqual(observer.SOURCE,ns['SOURCE']);self.assertEqual(observer.BOM,ns['DIGEST'])
        self.assertEqual(files,ns['files']())
        self.assertEqual({'pg4734_watch_parent.py','pg457_stable_actor.py','pg462_observer_identity.py','pg4216_same_peer_observer_manager.py'},set(files))
        for name,raw in files.items():
            self.assertEqual(0,check(raw,name));compile(raw,name,'exec')
        self.assertIn('reader.read(UNITS[role])',files['pg4734_watch_parent.py'])
        self.assertIn('observerTenMetadataRefsNormalClose',files['pg4734_watch_parent.py'])
        self.assertIn('pg4728-ssc299-publication-independent-post-v1',observer.source())
        self.assertIn('PG4702',observer.source())
        self.assertNotIn('PG3976',observer.source());self.assertNotIn('pg4552-failed-current',observer.source())
        for path in [observer.__file__,__file__]:self.assertEqual(0,checkPath(path))


if __name__=='__main__':unittest.main()
