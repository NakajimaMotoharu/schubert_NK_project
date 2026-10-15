import unittest
from pg3292_protocol_golden_canonical import area_bytes, vector_row


class IndependentCanonicalGoldenTest(unittest.TestCase):
    def test_literal_minimum_maximum_error_fixed_not_production(self):
        fields = [('text', 1, 3, 'X', 'M', 'text'), ('number', 4, 2, 'N', 'M', 'range'), ('flag', 6, 1, 'B', 'M', '0/1'), ('optional', 7, 2, 'X', 'O', 'optional'), ('kind', 9, 8, 'X', 'F', '固定`REQUEST`'), ('Reserved', 17, 1, 'X', 'F', 'Space')]
        self.assertEqual(b'A  000  REQUEST  ', area_bytes(fields))
        self.assertEqual(b'ZZZ991ZZREQUEST  ', area_bytes(fields, maximum=True))
        self.assertEqual(b'   00   REQUEST  ', area_bytes(fields, error=True))
        self.assertEqual(b'', area_bytes([]))

    def test_unknown_fixed_gap_width_type_and_boolean_rejected(self):
        for row in [('x', 2, 1, 'X', 'M', 'x'), ('x', 1, 0, 'X', 'M', 'x'), ('x', 1, 1, 'Z', 'M', 'x'), ('x', 1, 1, 'X', 'Z', 'x'), ('x', 1, 2, 'B', 'M', 'x'), ('x', 1, 2, 'X', 'F', 'guess'), ('x', 1, 1, 'X', 'F', '固定`REQUEST`')]:
            with self.subTest(row=row), self.assertRaises(ValueError):
                area_bytes([row])

    def test_only_response_has_error_hash_with_empty_areas(self):
        request = vector_row('AAA', {'AAA': ('Q',)}, {})
        response = vector_row('AAA', {'AAA': ('S',)}, {})
        self.assertEqual('-', request[-1])
        self.assertEqual('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', response[-1])


if __name__ == '__main__':
    unittest.main()
