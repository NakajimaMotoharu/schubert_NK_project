import unittest

from pg1540_debug_line_delta import positions, verify
from pg1540_debug_line_delta_test import fixture
from pg3409_related_qualification import verify_switch_debug


def one_line_fixture(line):
    # Independent handwritten class framing: retain exactly the first LNT entry.
    raw = bytearray(fixture(line)); locs = positions(bytes(raw))
    second = locs[1] - 2
    del raw[second:second + 4]
    # This fixture has nested Code/LNT lengths at fixed independently specified offsets.
    # Locate attributes by the known handcrafted fixture layout, not Production output.
    first = locs[0]
    raw[first - 4:first - 2] = (1).to_bytes(2, 'big')
    raw[first - 8:first - 4] = (6).to_bytes(4, 'big')
    code_length_offset = first - 28
    old_size = int.from_bytes(raw[code_length_offset:code_length_offset + 4], 'big')
    raw[code_length_offset:code_length_offset + 4] = (old_size - 4).to_bytes(4, 'big')
    return bytes(raw)


class SwitchDebugTest(unittest.TestCase):
    def test_real_boundary_and_every_non_line_mutation(self):
        old, new = one_line_fixture(154), one_line_fixture(158)
        self.assertEqual(verify_switch_debug(old, new)['lineOffset'], 4)
        loc = positions(old)[0]
        for i in range(len(new)):
            if i in [loc, loc + 1]:
                continue
            wrong = bytearray(new); wrong[i] ^= 1
            with self.subTest(offset=i), self.assertRaises((ValueError, UnicodeDecodeError)):
                verify_switch_debug(old, bytes(wrong))
        for wrong in [None, old, one_line_fixture(157), new[:-1], new + b'\0', fixture(158)]:
            with self.assertRaises((ValueError, UnicodeDecodeError)):
                verify_switch_debug(old, wrong)
        with self.assertRaises(ValueError):
            verify(old, new)


if __name__ == '__main__':
    unittest.main()
