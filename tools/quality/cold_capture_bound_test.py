import unittest
from cold_capture_bound import accepted


class CaptureBoundTest(unittest.TestCase):
    def test_explicit_size_boundaries(self):
        self.assertTrue(accepted(0,33554432,33554432))
        self.assertFalse(accepted(0,33554433,33554432))
        self.assertTrue(accepted(0,36343264,67108864))
        self.assertTrue(accepted(0,67108864,67108864))
        self.assertFalse(accepted(0,67108865,67108864))

    def test_unknown_negative_failed_and_bool(self):
        for values in [(None,1,10),(True,1,10),(1,1,10),(-1,1,10),(0,None,10),
                       (0,True,10),(0,-1,10),(0,1,None),(0,1,False),(0,1,0),(0,1,-1)]:
            with self.subTest(values=values):self.assertFalse(accepted(*values))


if __name__=='__main__':unittest.main()
