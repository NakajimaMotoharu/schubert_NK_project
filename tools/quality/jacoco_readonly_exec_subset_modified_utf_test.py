"""Independent vectors for the pinned writer's modified UTF field encoding."""

from struct import pack
import unittest

from jacoco_readonly_exec_subset import decode

HEADER = bytes.fromhex('01 c0c0 1007')
TIMES = pack('>qq', 1, 2)
WRITER_UNITS = bytes.fromhex('c080 01 7f c280 dfbf e0a080 eda080 eda0bd edb880')


def session(label):
    return b'\x10' + pack('>H', len(label)) + label + TIMES


def record(identity, name):
    return b'\x11' + pack('>QH', identity, len(name)) + name + b'\x01\x01'


class ModifiedUtfFieldTest(unittest.TestCase):
    def test_writer_code_units_remain_raw(self):
        stream = HEADER + session(WRITER_UNITS) + record(1, b'X') + record(2, WRITER_UNITS)
        self.assertEqual(
            {
                'classes': {'X': {
                    'crc64': '1', 'probeCount': 1, 'hitProbeIds': [0], 'missedProbeIds': [],
                }},
                'sessions': [{
                    'labelBytesHex': 'c080017fc280dfbfe0a080eda080eda0bdedb880',
                    'startMillis': 1,
                    'endMillis': 2,
                }],
                'totalClassRecords': 2,
            },
            decode(stream, {'X'}),
        )

    def test_writer_zero_length_field_keeps_exact_target(self):
        stream = HEADER + session(b'') + record(1, b'X') + record(2, b'')
        result = decode(stream, {'X'})
        self.assertEqual('', result['sessions'][0]['labelBytesHex'])
        self.assertEqual([0], result['classes']['X']['hitProbeIds'])
        self.assertEqual(2, result['totalClassRecords'])

    def test_session_field_rejects_impossible_writer_bytes(self):
        for payload in ('00', '80', 'c081', 'c1bf', 'c241', 'e09fbf', 'e0a0', 'e14180', 'f09f9880'):
            with self.subTest(payload=payload):
                stream = HEADER + session(bytes.fromhex(payload)) + record(1, b'X')
                with self.assertRaisesRegex(ValueError, 'invalid modified UTF field'):
                    decode(stream, {'X'})

    def test_nonselected_name_rejects_impossible_writer_bytes(self):
        for payload in ('00', '80', 'c081', 'c1bf', 'c241', 'e09fbf', 'e0a0', 'e14180', 'f09f9880'):
            with self.subTest(payload=payload):
                stream = HEADER + session(b'RUN') + record(1, b'X') + record(2, bytes.fromhex(payload))
                with self.assertRaisesRegex(ValueError, 'invalid modified UTF field'):
                    decode(stream, {'X'})
