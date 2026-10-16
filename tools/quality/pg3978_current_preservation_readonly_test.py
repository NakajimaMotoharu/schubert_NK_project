"""Fixed latest after11 remains data; no10field schema coercion or VM action."""
import unittest
from pyflakes.api import check
import pg3978_current_preservation_readonly as reader


class CurrentReadonly(unittest.TestCase):
    def test_full_namespace_current_after_native_and_no_actions(self):
        raw = reader.payload(); self.assertEqual(0, check(raw, '<fresh current full11 reader>'))
        for value in [reader.CURRENT, reader.BOM, reader.AFTER_SHA, "len(expected)==11", "==46)", 'native46Preserved', "read_rows()==first", "stateChangingActions':0"]:
            self.assertIn(value, raw)
        for value in ['pg3662-native-stop-v1', 'native34Preserved', 'daemon-reload', "'start'", "'stop'", 'pg3976-manifest']:
            self.assertNotIn(value, raw)


if __name__ == '__main__': unittest.main()
