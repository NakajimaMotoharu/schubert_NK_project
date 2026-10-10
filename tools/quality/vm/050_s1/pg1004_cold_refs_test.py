"""Independent ownership order and unknown-close negative cases; no Unit starts."""
import unittest
from pg1004_cold_refs import with_references
from pg1004_cold_readonly_v3 import source

class ScopeTest(unittest.TestCase):
    def test_reverse_return_and_failure_stays_failure(self):
        events=[]
        class Endpoint:
            fail=None
            def LoadUnit(self,n):events.append('load '+n)
            def RefUnit(self,n):
                events.append('ref '+n)
                if self.fail==n:raise OSError('ref unknown')
            def UnrefUnit(self,n):events.append('unref '+n)
            def close(self):events.append('close')
        endpoint=Endpoint()
        def body():events.append('body');return 17
        self.assertEqual(17,with_references(endpoint,endpoint,['a','b'],body))
        self.assertEqual(['load a','ref a','load b','ref b','body','unref b','unref a','close'],events)
        events.clear();endpoint.fail='b'
        with self.assertRaises(OSError):with_references(endpoint,endpoint,['a','b'],body)
        self.assertEqual(['load a','ref a','load b','ref b','unref a','close'],events)

    def test_each_owned_close_attempted_and_never_successful_if_unknown(self):
        for point in ['body','unref','bus']:
            events=[]
            class Endpoint:
                def LoadUnit(self,n):pass
                def RefUnit(self,n):pass
                def UnrefUnit(self,n):
                    events.append('unref '+n)
                    if point=='unref':raise OSError('unref unknown')
                def close(self):
                    events.append('close')
                    if point=='bus':raise OSError('bus unknown')
            e=Endpoint()
            def body():
                if point=='body':raise OSError('body unknown')
                return 0
            with self.assertRaises(OSError):with_references(e,e,['a','b'],body)
            self.assertEqual(['unref b','unref a','close'],events)
        raw=source()
        self.assertTrue("first=with_references(metadata_manager,metadata_bus,list(old['units']),observe_pair)"in raw)
        self.assertTrue("'run':'PG1004-cold-readonly-v3'"in raw)
        self.assertFalse('PG1003-cold-readonly-v2'in raw)

if __name__=='__main__':unittest.main()
