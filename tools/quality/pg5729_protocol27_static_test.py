"""BUG1477/YKT1239: display-only CP normalization never hides semantic changes."""
import unittest
from pg5729_protocol27_static import normalize_contract


class ContractNormalizationTest(unittest.TestCase):
    def test_cp_index_and_comment_padding_only_are_equivalent(self):
        a='24: ldc #94                 // String SYNC_REPLY_WEB\n'
        b='24: ldc #105                // String SYNC_REPLY_WEB\n'
        self.assertEqual(normalize_contract(a),normalize_contract(b))

    def test_semantic_mutations_remain_visible(self):
        a='24: ldc #94                 // String SYNC_REPLY_WEB\n'
        for b in (a.replace('ldc','getstatic'),a.replace('SYNC_REPLY_WEB','OTHER'),
                  'public java.lang.String other();\n'+a,a.replace('24:','25:')):
            with self.subTest(mutant=b):self.assertNotEqual(normalize_contract(a),normalize_contract(b))

    def test_only_declared_private_field_names_are_normalized(self):
        self.assertEqual(normalize_contract('getfield #1 // Field encodedAddress:Ljava/lang/String;'),
                         normalize_contract('getfield #91 // Field address:Ljava/lang/String;'))
        self.assertNotEqual(normalize_contract('public void changed();'),normalize_contract('public void original();'))


if __name__=='__main__':unittest.main()
