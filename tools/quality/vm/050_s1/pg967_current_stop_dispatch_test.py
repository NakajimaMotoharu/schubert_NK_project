"""No VM effects: independent pins for the new source/proof/freeze dispatch."""
import unittest
import pg965_current_stop_compile as c
import pg966_current_owned_stop as d
class Test(unittest.TestCase):
    def test_frozen_source_and_new_proofs(self):
        s=c.source()
        for x in ('pg963_current_stop_binding','pg964_current_stop_test','pg960-completed-readonly-v1','pg961-chr-a01-native-v1','pg932-release-v1','Pg963NativeStop.java','Pg963NativeArgumentTest.java'):
            self.assertIn(x,s,'missing '+x)
        self.assertNotIn('pg875',s);self.assertNotIn('pg862-release',s)
    def test_dispatch_never_reuses_old_proof_or_slots(self):
        s=d.source()
        for x in ('pg963_current_stop_binding','pg960-completed-readonly-v1','pg961-chr-a01-native-v1','pg963-native-tools-v1','Pg963NativeStop stop'):
            self.assertIn(x,s,'missing '+x)
        for old in ('pg877','Pg877','pg875','pg876','pg862'):self.assertNotIn(old,s)
if __name__=='__main__':unittest.main()
