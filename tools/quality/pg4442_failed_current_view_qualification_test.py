"""Object order is nonsemantic, every value/type/cursor/event order remains exact."""
import unittest
from pg4442_failed_current_view_qualification import strict_equal, journal_rows


class JournalAllValues(unittest.TestCase):
    def test_independent_literal_key_order_only_and_every_other_difference_rejected(self):
        first = b'{"__CURSOR":"a","X":"fixed","LIST":[1,"two"]}\n{"__CURSOR":"b","X":"next"}\n'
        second = b'{"LIST":[1,"two"],"X":"fixed","__CURSOR":"a"}\n{"X":"next","__CURSOR":"b"}\n'
        literal = [{'__CURSOR':'a','X':'fixed','LIST':[1,'two']},{'__CURSOR':'b','X':'next'}]
        self.assertTrue(strict_equal(literal, journal_rows(first))); self.assertTrue(strict_equal(literal, journal_rows(second)))
        self.assertNotEqual(first, second)
        for bad in [first.replace(b'fixed', b'changed'), first.replace(b'1,"two"', b'"two",1'), first.replace(b'"a"', b'"other"'), first.replace(b',"X":"fixed"', b''), first.replace(b'[1,', b'[true,')]:
            self.assertFalse(strict_equal(literal, journal_rows(bad)))
        self.assertFalse(strict_equal(literal, list(reversed(journal_rows(first)))))
        for bad in [b'{"X":"missing"}\n', b'{"__CURSOR":"a","__CURSOR":"b"}\n', first + first]:
            with self.assertRaises(ValueError): journal_rows(bad)


if __name__ == '__main__':
    unittest.main()
