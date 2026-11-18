"""TOOL-COVERAGE-SESSION008..014, independent Java signed-long and exact-name vectors."""
import unittest

from coverage_session_schema import parse


class CoverageSessionSchemaTest(unittest.TestCase):
    def test_008_java_long_zero_and_maximum_are_valid(self):
        self.assertEqual(
            {'sessionId': 'fixture', 'startMillis': 0, 'endMillis': 9223372036854775807},
            parse(['SESSION', 'fixture', '0', '9223372036854775807'], 'fixture'),
        )
        self.assertEqual(
            {'sessionId': 'fixture', 'startMillis': 9223372036854775807, 'endMillis': 9223372036854775807},
            parse(['SESSION', 'fixture', '9223372036854775807', '9223372036854775807'], 'fixture'),
        )

    def test_009_rejects_overflow_in_dump_timestamp(self):
        with self.assertRaisesRegex(ValueError, 'outside Java long range'):
            parse(['SESSION', 'fixture', '0', '9223372036854775808'], 'fixture')

    def test_010_rejects_overflow_in_start_timestamp(self):
        with self.assertRaisesRegex(ValueError, 'outside Java long range'):
            parse(['SESSION', 'fixture', '9223372036854775808', '9223372036854775808'], 'fixture')

    def test_011_rejects_empty_name_even_when_both_fields_match(self):
        with self.assertRaisesRegex(ValueError, 'nonempty session name'):
            parse(['SESSION', '', '0', '1'], '')

    def test_012_rejects_nontext_names_even_when_both_fields_match(self):
        for name in (None, 7):
            with self.subTest(name=name):
                with self.assertRaisesRegex(ValueError, 'nonempty session name'):
                    parse(['SESSION', name, '0', '1'], name)

    def test_013_preserves_previous_leading_zero_decimal_values(self):
        self.assertEqual(
            {'sessionId': 'fixture', 'startMillis': 0, 'endMillis': 9223372036854775807},
            parse(['SESSION', 'fixture', '0000', '0009223372036854775807'], 'fixture'),
        )

    def test_014_rejects_oversized_numbers_before_integer_conversion(self):
        with self.assertRaisesRegex(ValueError, 'outside Java long range'):
            parse(['SESSION', 'fixture', '0', '9' * 5_000], 'fixture')


if __name__ == '__main__':
    unittest.main()
