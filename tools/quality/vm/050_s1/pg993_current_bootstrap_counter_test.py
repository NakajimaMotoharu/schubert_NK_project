"""Independent same-source/stream count/one process two dumps/proof run pins."""
import unittest
import pg992_current_bootstrap_native_counter as p
class Test(unittest.TestCase):
    def test_current_qualified_ten_and_no_previous_sixteen(self):
        raw=p.source()
        for x in ('40ef6e894573d2ffab1d1732124960f9c98d5f97','pg926-body-six-host-v1','pg972-current-eight-native-v2','043e7c88400840fd945512548c70a2d8dda2e53a6d9e2f6b5b5855bd0bab3d8b',"post['run']=='PG989-bootstrap-post-v4'",'len(prior)==8',"'currentNativeStreams':10","'bootstrapSameProcessDumps':2",'new_sessions[0]',"'otherSourceNativeImported':0",'classByteMismatch'):
            self.assertTrue(x in raw,'missing '+x)
        for old in ('pg903','pg892','pg894','pg901','pg857',"'currentNativeStreams':18"):
            self.assertFalse(old in raw,'old '+old)
        self.assertTrue("'distinctCurrentJvmExecutions':9" in raw)
        self.assertTrue("'distinctOsProcessCount':None" in raw)
if __name__=='__main__':unittest.main()
