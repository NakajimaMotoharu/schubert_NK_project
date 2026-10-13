"""Same full3635/native point/window and current Main qualification closure."""
import unittest
import pg2384_current_resume_native_qualification as p


class Qualification(unittest.TestCase):
    def test_actual_server_transport_single_latest_inspector(self):
        s=p.server();t=p.source()
        for n in ['PG2384-native-v1','source-full-PG2300','runs/PG2300-six-v1','3635',p.SOURCE,'classByteMismatch','NativePointDominance','len(streams)==9','if i!=early_index','inspectorLatestClosingOnly']:self.assertIn(n,s)
        for n in ['pg2382-current-resume-native-catalog-v1','pg2384-current-resume-native-qualified-v1','pg2301-jdbc-host-integration-qualified-v1','NativePointDominance.java','NativePointDominanceTest.java']:self.assertIn(n,t)
        for n in ['PG2256','source-full-PG2228','3633','0fd734']:self.assertNotIn(n,s)
        self.assertEqual(s,p.entry().__globals__['CODE'])
        self.assertEqual(p.SOURCE,p.entry().__globals__['SOURCE'])


if __name__=='__main__':unittest.main()
