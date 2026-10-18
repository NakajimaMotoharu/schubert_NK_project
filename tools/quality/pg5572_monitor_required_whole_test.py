import inspect
import unittest
from pyflakes.api import check,checkPath
import pg5572_monitor_required_whole as entry


class MonitorWhole(unittest.TestCase):
    def test_complete_standalone_and_genuine3904_not_confirmation(self):
        raw=entry.server_source(entry.SOURCE,'a'*64)
        self.assertEqual(check(raw,'<whole3904 complete>'),0)
        self.assertIn('PG5572',raw);self.assertNotIn('PG5550',raw)
        self.assertIn('3904',raw);self.assertIn('563',raw);self.assertIn('1664',raw)
        self.assertIn('format-before-pt',raw)

    def test_original_success_post_source_guards_before_fresh_dispatch(self):
        raw=inspect.getsource(entry.prerequisites)
        for literal in("selected['actualCases']==71","proof['actualExit']==0","==14","==11",'canonical2fc'):
            self.assertIn(literal,raw)
        main=inspect.getsource(entry.main)
        self.assertLess(main.index('prerequisites()'),main.index('fresh=previous.preflight()'))
        self.assertLess(main.index('fresh=previous.preflight()'),main.index("scope['main']()"))
        for path in(entry.__file__,__file__):self.assertEqual(checkPath(path),0)


if __name__=='__main__':unittest.main()
