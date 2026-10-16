import ast
import unittest
import pg3798_hygiene_current_observer as observer
import pg3800_hygiene_browser_ready as browser


class CurrentObserver(unittest.TestCase):
    def test_frozen_source_roles_no_business_actions(self):
        raw=observer.source();ast.parse(raw)
        for marker in [observer.SOURCE,observer.BOM,'PG3748','pg3794-hygiene-publication-independent-post-v1','pg3798']:self.assertTrue(marker in raw,marker)
        for marker in ['pg3462','PG3420','systemctl start','systemctl stop']:self.assertFalse(marker in raw,marker)
        values=observer.namespace()['files']();self.assertEqual(3,len(values))
        for name,text in values.items():compile(text,'<readonly observer '+name+'>','exec')
        self.assertEqual(observer.SOURCE,browser.SOURCE)
        self.assertIn('tools/quality/pg3800_hygiene_browser_ready.py',browser.PINNED)


if __name__=='__main__':unittest.main()
