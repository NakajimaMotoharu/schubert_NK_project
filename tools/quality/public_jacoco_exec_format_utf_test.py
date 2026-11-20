"""Independent canonical writer vectors for the public coverage format audit."""

from struct import pack
import unittest

from public_jacoco_exec_format_v1 import fixtures, parse


HEADER = bytes.fromhex("01 c0c0 1007")
TIMES = pack(">qq", 1, 2)
PROBES = bytes.fromhex("03 05")


def stream(label, owner):
    return (
        HEADER + b"\x10" + pack(">H", len(label)) + label + TIMES
        + b"\x11" + pack(">QH", 42, len(owner)) + owner + PROBES
    )


class PublicExecModifiedUtfTest(unittest.TestCase):
    def test_exec_utf_001_rejects_invalid_writer_bytes_in_each_field(self):
        invalid = ("c181", "e08181", "00", "c081", "e0a0", "f09f9880")
        for encoding in invalid:
            raw = bytes.fromhex(encoding)
            for field, value in (("session", stream(raw, b"A")), ("class", stream(b"A", raw))):
                with self.subTest(field=field, encoding=encoding):
                    with self.assertRaisesRegex(ValueError, "^invalid modified UTF field$"):
                        parse(value)

    def test_exec_utf_002_keeps_canonical_code_unit_counts(self):
        units = bytes.fromhex("41 7f c080 c280 dfbf e0a080 eda0bd edb880")
        data = stream(units, units)
        self.assertEqual(
            {
                "bytes": len(data), "headers": 1, "sessions": 1, "classes": 1,
                "probes": 3, "hits": 2, "sessionUnits": 8, "classUnits": 8,
                "asciiSessions": 0, "asciiClasses": 0, "orderedSessions": 1,
                "unusedPaddingSetBits": 0, "consumedBytes": len(data),
            },
            parse(data),
        )

    def test_exec_utf_003_preserves_original_format_and_type_oracles(self):
        positive, negative = fixtures()
        self.assertEqual((5, 14), (len(positive), len(negative)))
        for case, data, expected in positive:
            with self.subTest(case=case):
                self.assertEqual(expected, parse(data))
        for case, data in negative:
            with self.subTest(case=case):
                with self.assertRaises(ValueError):
                    parse(data)
        for invalid_type in (None, "PUBLIC", False, bytearray(HEADER)):
            with self.assertRaises(ValueError):
                parse(invalid_type)
