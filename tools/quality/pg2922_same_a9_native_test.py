"""No foreign exec source, no guest read; all members before native rejoin."""
import unittest
import pg2922_same_a9_native_rejoin as p


class SameNativeRejoin(unittest.TestCase):
    def test_completed_member_and_cached_byte_contract(self):
        a=p.server();b=p.source()
        for value in ['PG2918','3684','oldmembers==newmembers','identical_main==1643','PG2922-native-v1']:
            self.assertTrue(value in a,value)
        self.assertNotIn('subprocess.run(SSH',b)
        self.assertIn("native_input['selected']!=catalog['selected']",b)
        self.assertIn("sha(cached)!=v['sha256']",b)
        self.assertIn("data['nativeQualifiedFull']=native_input['qualifiedFull']",b)


if __name__=='__main__':unittest.main()
