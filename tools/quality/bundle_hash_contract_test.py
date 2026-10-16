import unittest
from bundle_hash_contract import unbind,require_bound


class Bundle(unittest.TestCase):
    def test_unbound_bound_noop_duplicate_nested_foreign_and_data_preservation(self):
        raw="BUNDLE_HASH='"+'a'*64+"'\nnegative='323bc9ad-1528-449a-8067-19228ee1e046'\nrows={'old':'"+'a'*64+"'}\ndef read():return BUNDLE_HASH\n";plain=raw.split('\n',1)[1];self.assertEqual(plain,unbind(raw));bound="BUNDLE_HASH='"+'b'*64+"'\n"+plain;self.assertTrue(require_bound(bound,'b'*64))
        for bad in [plain,bound+raw.split('\n',1)[0]+'\n',bound.replace('b'*64,'c'*64),"if True:\n BUNDLE_HASH='"+'b'*64+"'\n", "BUNDLE_HASH:str='"+'b'*64+"'\n"]:
            with self.assertRaises(ValueError):require_bound(bad,'b'*64)
        for bad in [plain,raw+raw.split('\n',1)[0]+'\n',"BUNDLE_HASH=None\n"]:
            with self.assertRaises(ValueError):unbind(bad)


if __name__=='__main__':unittest.main()
