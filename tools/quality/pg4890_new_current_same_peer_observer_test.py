import unittest
from pyflakes.api import check,checkPath
import pg4890_new_current_same_peer_observer as role


class Observer(unittest.TestCase):
    def test_actual_four_files_source_bom_and_same_peer_lifetime_contract(self):
        values=role.files();ns=role.namespace()
        self.assertEqual(role.SOURCE,ns['SOURCE']);self.assertEqual(role.BOM,ns['DIGEST'])
        self.assertEqual(values,ns['files']())
        self.assertEqual({'pg4890_watch_parent.py','pg457_stable_actor.py','pg462_observer_identity.py','pg4216_same_peer_observer_manager.py'},set(values))
        for name,raw in values.items():self.assertEqual(0,check(raw,name));compile(raw,name,'exec')
        for text in ('reader.read(UNITS[role])','observerTenMetadataRefsNormalClose'):self.assertIn(text,values['pg4890_watch_parent.py'])
        self.assertIn('pg4886-ssc301-302-publication-independent-post-v1',role.source());self.assertIn('PG4860',role.source());self.assertNotIn('PG4702',role.source())
        self.assertEqual(0,checkPath(role.__file__));self.assertEqual(0,checkPath(__file__))


if __name__=='__main__':unittest.main()
