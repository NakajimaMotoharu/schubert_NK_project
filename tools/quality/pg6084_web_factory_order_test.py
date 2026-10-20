import unittest
from pg6084_web_factory_order import narrow_or_wide_literal_body, factory_owner


class OwnershipFactsTest(unittest.TestCase):
    def test_literal_width_normalization_preserves_branch_and_exception_targets(self):
        a = ' 0: ldc #CP // String fixed\n 2: goto 5\n 5: return\n Exception table:\n 0 2 5 any\n'
        b = ' 0: ldc_w #CP // String fixed\n 3: goto 6\n 6: return\n Exception table:\n 0 3 6 any\n'
        self.assertEqual(narrow_or_wide_literal_body(a), narrow_or_wide_literal_body(b))
        self.assertNotEqual(narrow_or_wide_literal_body(a), narrow_or_wide_literal_body(b.replace('String fixed', 'String changed')))
        self.assertNotEqual(narrow_or_wide_literal_body(a), narrow_or_wide_literal_body(b.replace('goto 6', 'goto 3')))
        self.assertNotEqual(narrow_or_wide_literal_body(a), narrow_or_wide_literal_body(b.replace('0 3 6 any', '0 3 3 any')))

    def test_missing_owner_is_not_accepted(self):
        with self.assertRaises(ValueError):
            factory_owner({})


if __name__ == '__main__':
    unittest.main()
