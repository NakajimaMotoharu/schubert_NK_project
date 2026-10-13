import unittest
import pg2256_newboot_native_qualification as p


class CurrentNativeQualification(unittest.TestCase):
    def test_one_currentboot_catalog_full_source_and_server_namespace(self):
        s=p.server();t=p.source()
        for v in ['PG2256-native-v1','source-full-PG2228','runs/PG2228-six-v1','3633',p.SOURCE,'classByteMismatch']:self.assertIn(v,s)
        for v in ['pg2254-newboot-native-catalog-v1','pg2256-newboot-native-qualified-v1','pg2236-root-host-integration-full-qualified-v1']:self.assertIn(v,t)
        for v in ['source-full-PG2124','PG2198-native-v1','3631']:self.assertNotIn(v,s)
        self.assertEqual(s,p.entry().__globals__['CODE'])
        self.assertEqual(p.SOURCE,p.entry().__globals__['SOURCE'])
        for v in ['NativePointDominance','len(streams)==9','if i!=early_index','inspectorLatestClosingOnly','validatedNativePoints']:
            self.assertIn(v,s)
        self.assertIn('NativePointDominance.java',t)
        self.assertIn('NativePointDominanceTest.java',t)


if __name__=='__main__':unittest.main()
