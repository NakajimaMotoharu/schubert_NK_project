"""No foreign exec source, no guest read; all members before native rejoin."""
import unittest
import pg2922_same_a9_native_rejoin as p


class SameNativeRejoin(unittest.TestCase):
    def test_completed_member_and_cached_byte_contract(self):
        a=p.server();b=p.source()
        for value in ['PG2918','3684','member_counts(oldmembers,newmembers)','identical_main==1643','PG2922-native-v1']:
            self.assertTrue(value in a,value)
        self.assertNotIn('subprocess.run(SSH',b)
        self.assertIn("native_input['selected']!=catalog['selected']",b)
        self.assertIn("sha(cached)!=v['sha256']",b)
        self.assertIn("data['nativeQualifiedFull']=native_input['qualifiedFull']",b)

    def test_same_member_bytes_and_class_resource_meta_deltas(self):
        old={'NativeIo.class':b'byte and debug lines','layout.bin':b'fixed64','META-INF/MANIFEST.MF':b'fixed version'}
        self.assertEqual((1,2),p.member_counts(old,dict(old)))
        for key in old:
            changed={**old,key:b'different'}
            with self.assertRaises(ValueError):p.member_counts(old,changed)
            missing=dict(old);del missing[key]
            with self.assertRaises(ValueError):p.member_counts(old,missing)
        for new in [None,{}, {**old,'extra.class':b'extra'}]:
            with self.assertRaises(ValueError):p.member_counts(old,new)
        with self.assertRaises(ValueError):p.member_counts({'Bad.class':'not bytes'},{'Bad.class':'not bytes'})


if __name__=='__main__':unittest.main()
