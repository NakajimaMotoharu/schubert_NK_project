"""Independent 0x1007 stream evidence checks, separate from the signed-time suite."""
import struct
import unittest

from jacoco_readonly_exec_subset import decode

HEADER = bytes.fromhex('01c0c01007')
SESSION = b'\x10\x00\x03RUN' + struct.pack('>qq', 1, 2)
ONE_PROBE = b'\x01\x01'


def record(crc, name, probe_data=ONE_PROBE):
    return b'\x11' + struct.pack('>QH', crc, len(name)) + name + probe_data


class RecordPresenceTest(unittest.TestCase):
    def test_absent_target_is_not_a_zero_probe_report(self):
        payload = HEADER + SESSION + record(1, b'Other')
        with self.assertRaisesRegex(ValueError, 'all exact target records required'):
            decode(payload, {'Chosen'})

    def test_target_name_with_conflicting_crc_stays_unqualified(self):
        payload = HEADER + SESSION + record(1, b'Chosen') + record(2, b'Chosen')
        with self.assertRaisesRegex(ValueError, 'one target class identity only'):
            decode(payload, {'Chosen'})

    def test_two_names_for_one_crc_stay_unqualified(self):
        payload = HEADER + SESSION + record(1, b'Chosen') + record(1, b'Other')
        with self.assertRaisesRegex(ValueError, 'no duplicate class record union'):
            decode(payload, {'Chosen'})

    def test_missing_session_does_not_qualify_a_present_class(self):
        payload = HEADER + record(1, b'Chosen')
        with self.assertRaisesRegex(ValueError, 'one session and all exact target records required'):
            decode(payload, {'Chosen'})

    def test_compact_count_outside_java_int_does_not_read_probe_data(self):
        payload = HEADER + SESSION + record(1, b'Chosen', bytes.fromhex('8080808008'))
        with self.assertRaisesRegex(ValueError, 'nonnegative Java int count required'):
            decode(payload, {'Chosen'})

    def test_unsigned_crc_and_probe_bits_keep_exact_identity(self):
        nine_probes = b'\x09\x01\x01'
        payload = HEADER + SESSION + record(0xffffffffffffffff, b'Chosen', nine_probes)
        payload += record(1, b'Other')
        observed = decode(payload, {'Chosen'})
        self.assertEqual(2, observed['totalClassRecords'])
        self.assertEqual({'Chosen': {
            'crc64': 'ffffffffffffffff',
            'probeCount': 9,
            'hitProbeIds': [0, 8],
            'missedProbeIds': [1, 2, 3, 4, 5, 6, 7],
        }}, observed['classes'])

    def test_mutable_input_is_outside_readonly_contract(self):
        with self.assertRaisesRegex(ValueError, 'immutable bytes'):
            decode(bytearray(HEADER + SESSION + record(1, b'Chosen')), {'Chosen'})

    def test_unicode_names_are_outside_explicit_ascii_subset(self):
        with self.assertRaisesRegex(ValueError, 'explicit ASCII target names'):
            decode(HEADER + SESSION + record(1, b'Chosen'), {'対象'})


if __name__ == '__main__':
    unittest.main()
