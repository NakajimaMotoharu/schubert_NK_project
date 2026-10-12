"""Independent exactly-once command/Ref lifetime/source/native preservation joins."""
import unittest
from pyflakes.api import check
import pg1699_new_current_ordinary_once as p
from pg1698_new_current_ordinary_observer import namespace


class NewOrdinaryOnceTest(unittest.TestCase):
    def test_same_source_immutable_observer_and_start_inside_refs(self):
        files=namespace()['files']();self.assertIn('pg1698_watch_parent.py',files)
        raw=p.payload({n:'a'*64 for n in files})
        self.assertEqual(0,check(raw,'<new source normal once>'))
        command="'/usr/bin/systemctl','start','--no-block','schubert-nk-morning-controller.service'"
        self.assertEqual(1,raw.count(command))
        self.assertLess(raw.index(command),raw.rindex('finally:'))
        self.assertIn('require(len(records)==14)',raw)
        self.assertIn('2741c4546afad6c1e8b6efbd53dfb58144edf7bb',raw)
        self.assertIn('195e0668bc5a1fea2cbf2a93747e0cdcbf1bcb66c3f3f23a362fca7c89ae82e1',raw)
        self.assertIn('pg1699-new-current-ordinary-once-v1',raw)
        self.assertIn('replayAllowed',raw)
        self.assertNotIn("after['native']",raw)
        self.assertNotIn('pidfd_send_signal',raw)
        self.assertNotIn("'--resume'",command)


if __name__=='__main__':unittest.main()
