import unittest
from pg3552_signed_main_java25 import java25_class


class IndependentClassVersionVector(unittest.TestCase):
    def test_java25_fixed_header(self):
        self.assertTrue(java25_class(bytes.fromhex('cafebabe00000045')))

    def test_null_missing_unknown_magic_and_wrong_major(self):
        for value in [None,b'',b'\xca\xfe\xba\xbe',bytes.fromhex('cafebabe00000044'),
                      bytes.fromhex('cafebabe00000046'),bytes.fromhex('deadbeef00000045'),'cafebabe00000045']:
            with self.subTest(value=value),self.assertRaises(ValueError):java25_class(value)


if __name__=='__main__':unittest.main()
