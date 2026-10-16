import unittest
from pg4058_original_read_profile_test import GuardTest
import pg4064_original_profile_typed_oid as profile


class OidTest(unittest.TestCase):
    def test_actual_oid_string_refused_integer_matches(self):
        v, ns, _ = GuardTest().fixture(True)
        ns['peers'](v, (140, 240))
        # Independent read-only PostgreSQL literal vector: to_jsonb(oid) is JSON string.
        v['database']['locks'][0].update(classid='0', objid='71419602')
        with self.assertRaises(ValueError): ns['peers'](v, (140, 240))
        v['database']['locks'][0].update(classid=0, objid=71419603)
        with self.assertRaises(ValueError): ns['peers'](v, (140, 240))

    def test_cast_and_compile_bytes_kept(self):
        raw = profile.payload('run')
        self.assertTrue('classid::bigint as classid,objid::bigint as objid' in raw)
        self.assertTrue("frozen/'compile.safe.json'" in raw and "compiled['classHashes']" in raw)
        self.assertFalse('subprocess.run(args,env=env' in raw, 'no compiler replay')
        self.assertTrue('pg4060-original-read-profile-v1' in raw and profile.SLOT in raw)
        with self.assertRaises(ValueError): profile.payload('compile')


if __name__ == '__main__': unittest.main()
