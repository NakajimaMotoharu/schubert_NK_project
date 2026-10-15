"""Independent Markdown parser counterexamples; zero Production PT/coverage credit."""
import unittest
import pg3284_protocol_canonical_fixtures as subject

DOC = '''## 2. Common `PAGED48`
PAGRSP01で使用。
| Page | 1 | 1 | N | M | fixed page |
## 3. Common `MEDIA1024`
AUDRSP01、VIDRSP01で使用。
| MIME | 1 | 4 | X | M | fixed MIME |
## 4. Common `USRMUT24`
UCRRSP01、ULKRSP01で使用。
| User ID | 1 | 2 | N | M | target |
### 5.1 `VIDRSP01` data
| MEDIA1024 | 1 | 4 | - | M | explicit shared descriptor |
| Title | 5 | 3 | X | M | title |
'''


class CanonicalFixtureParserTest(unittest.TestCase):
    def test_explicit_alias_before_japanese_text_and_composite_offsets(self):
        result = subject.field_areas([DOC])
        self.assertEqual([('User ID', 1, 2, 'N', 'M', 'target')], result[('ULKRSP01', 'DATA')])
        self.assertEqual([('Page', 1, 1, 'N', 'M', 'fixed page')], result[('PAGRSP01', 'DATA')])
        self.assertEqual([('MIME', 1, 4, 'X', 'M', 'fixed MIME'), ('Title', 5, 3, 'X', 'M', 'title')], result[('VIDRSP01', 'DATA')])

    def test_unknown_width_presence_wire_duplicate_and_missing_template_reject(self):
        for raw in [DOC.replace('| MEDIA1024 | 1 | 4 |', '| MEDIA1024 | 1 | 5 |'),
                    DOC.replace('| MEDIA1024 | 1 | 4 | - | M |', '| MEDIA1024 | 1 | 4 | - | O |'),
                    DOC.replace('| MIME | 1 | 4 | X |', '| MIME | 1 | 4 | Z |'),
                    DOC.replace('UCRRSP01、ULKRSP01', 'UCRRSP01、UCRRSP01'),
                    DOC + '### 5.2 `VIDRSP01` data\n',
                    DOC.replace('`PAGED48`', '`UNKNOWN`')]:
            with self.assertRaises(ValueError):
                subject.field_areas([raw])

    def test_independent_layout_formula_duplicate_and_bad_decimal_reject(self):
        row = '| IF-001 | Q `ABCReq01` | S | 1 | 0 | 0 | 257 |'
        self.assertEqual({}, subject.layouts(row))  # Canonical IDs are uppercase.
        row = row.replace('ABCReq01', 'ABCREQ01')
        self.assertEqual(('Q', 'S', 1, 0, 0, 257), subject.layouts(row)['ABCREQ01'])
        for raw in [row + '\n' + row, row.replace('257', '258'), row.replace('| 1 |', '| 1,00 |')]:
            with self.assertRaises(ValueError):
                subject.layouts(raw)

    def test_ss_java_mapping_is_explicit_not_inferred_from_production(self):
        row = '| `ABCRSP01` 1/2/3/263 | `ActualData` / `ActualRecord` | service |'
        self.assertEqual({'ABCRSP01': ('ActualData', 'ActualRecord')}, subject.named_types(row))
        with self.assertRaises(ValueError):
            subject.named_types(row + '\n' + row)
        with self.assertRaises(ValueError):
            subject.named_types(row.replace('`ActualRecord`', '`ActualRecord` / `WrongExtra`'))


if __name__ == '__main__':
    unittest.main()
