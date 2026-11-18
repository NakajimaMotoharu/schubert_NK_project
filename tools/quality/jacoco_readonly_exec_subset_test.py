"""Independent signed-long vectors for the JaCoCo 0x1007 read-only decoder."""
import struct
import unittest

import jacoco_readonly_exec_subset as decoder

JAVA_LONG_MAX = (1 << 63) - 1
JAVA_LONG_MIN = -(1 << 63)
HEADER = bytes.fromhex('01c0c01007')
CLASS = bytes.fromhex('1100000000000000010001580305')


def stream(start, end):
    return HEADER + b'\x10\x00\x03RUN' + struct.pack('>qq', start, end) + CLASS


class SessionTimeTest(unittest.TestCase):
    def test_original_decoder_vectors(self):
        self.assertEqual(12, decoder.selftest())

    def test_epoch_can_be_a_zero_length_session(self):
        actual, = decoder.decode(stream(0, 0), {'X'})['sessions']
        self.assertEqual({'labelBytesHex': '52554e', 'startMillis': 0, 'endMillis': 0}, actual)

    def test_latest_java_long_can_be_both_timestamps(self):
        actual, = decoder.decode(stream(JAVA_LONG_MAX, JAVA_LONG_MAX), {'X'})['sessions']
        self.assertEqual(JAVA_LONG_MAX, actual['startMillis'])
        self.assertEqual(JAVA_LONG_MAX, actual['endMillis'])

    def test_epoch_to_latest_java_long(self):
        actual, = decoder.decode(stream(0, JAVA_LONG_MAX), {'X'})['sessions']
        self.assertEqual(0, actual['startMillis'])
        self.assertEqual(JAVA_LONG_MAX, actual['endMillis'])

    def test_negative_start_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'ordered original session'):
            decoder.decode(stream(-1, 0), {'X'})

    def test_negative_end_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'ordered original session'):
            decoder.decode(stream(0, -1), {'X'})

    def test_two_minimum_java_longs_are_rejected(self):
        with self.assertRaisesRegex(ValueError, 'ordered original session'):
            decoder.decode(stream(JAVA_LONG_MIN, JAVA_LONG_MIN), {'X'})

    def test_two_negative_ones_are_rejected(self):
        with self.assertRaisesRegex(ValueError, 'ordered original session'):
            decoder.decode(stream(-1, -1), {'X'})

    def test_negative_end_cannot_be_greater_than_latest_java_long(self):
        with self.assertRaisesRegex(ValueError, 'ordered original session'):
            decoder.decode(stream(JAVA_LONG_MAX, JAVA_LONG_MIN), {'X'})


if __name__ == '__main__':
    unittest.main()
