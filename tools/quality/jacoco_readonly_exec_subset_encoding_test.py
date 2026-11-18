"""Fixed wire vectors for the writer's compact counts and probe-byte padding."""
import struct
import unittest

from jacoco_readonly_exec_subset import decode

HEADER = bytes.fromhex('01 c0c0 1007')
SESSION = bytes.fromhex('10 0003 52554e') + struct.pack('>qq', 1000, 1001)
X = bytes.fromhex('11 0000000000000001 0001 58')
Y = bytes.fromhex('11 0000000000000002 0001 59')


def target(record):
    return decode(HEADER + SESSION + record, {'X'})['classes']['X']


class CanonicalEncodingTest(unittest.TestCase):
    def test_rejects_nonminimal_zero(self):
        with self.assertRaisesRegex(ValueError, 'nonminimal compact count'):
            target(X + bytes.fromhex('80 00'))

    def test_rejects_nonminimal_three(self):
        with self.assertRaisesRegex(ValueError, 'nonminimal compact count'):
            target(X + bytes.fromhex('83 00 05'))

    def test_rejects_target_padding_above_last_probe(self):
        with self.assertRaisesRegex(ValueError, 'nonzero final probe padding'):
            target(X + bytes.fromhex('03 85'))

    def test_rejects_bad_padding_in_a_nonselected_record(self):
        with self.assertRaisesRegex(ValueError, 'nonzero final probe padding'):
            target(X + bytes.fromhex('01 01') + Y + bytes.fromhex('01 80'))

    def test_pinned_counts_at_zero_and_near_single_byte_limit(self):
        for count, tag in ((0, '00'), (127, '7f'), (129, '81 01')):
            with self.subTest(count=count):
                actual = target(X + bytes.fromhex(tag) + bytes((count + 7) // 8))
                self.assertEqual({'crc64': '1', 'probeCount': count, 'hitProbeIds': [],
                                  'missedProbeIds': list(range(count))}, actual)

    def test_full_probe_byte_and_partial_probe_byte(self):
        self.assertEqual(list(range(8)), target(X + bytes.fromhex('08 ff'))['hitProbeIds'])
        actual = target(X + bytes.fromhex('09 ff 01'))
        self.assertEqual(list(range(9)), actual['hitProbeIds'])
        self.assertEqual([], actual['missedProbeIds'])
