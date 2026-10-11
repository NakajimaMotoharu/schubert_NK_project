import types
import unittest
from pg1468_auth_cause_capture import stable
from pg1470_auth_cause_retry import source


class StableMetadataTest(unittest.TestCase):
    def test_atime_is_not_authority_each_fixed_field_stays_authority(self):
        fields=['st_dev','st_ino','st_mode','st_uid','st_gid','st_nlink',
                'st_size','st_mtime_ns','st_ctime_ns']
        base=dict(zip(fields,range(1,10)),st_atime_ns=100)
        expected=stable(types.SimpleNamespace(**base))
        self.assertEqual(expected,tuple(range(1,10)))
        self.assertEqual(expected,stable(types.SimpleNamespace(**(base|{'st_atime_ns':200}))))
        for name in fields:
            with self.subTest(name=name):
                self.assertNotEqual(expected,stable(types.SimpleNamespace(**(base|{name:base[name]+1}))))

    def test_fresh_namespace_only_and_raw_not_exported(self):
        raw=source();self.assertNotIn('PG1468',raw)
        self.assertIn("'rawExported':False",raw)
        self.assertIn('stat.S_IMODE(m.st_mode)==0o600',raw)


if __name__=='__main__':unittest.main()
