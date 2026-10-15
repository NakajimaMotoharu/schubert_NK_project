import unittest
from source_utf16 import source_slice


class Utf16(unittest.TestCase):
    def test_literal_ascii_japanese_supplementary_and_empty_boundaries(self):
        self.assertEqual('0600',source_slice('x😀0600',3,7))
        self.assertEqual('日本',source_slice('😀日本😀',2,4))
        self.assertEqual('😀',source_slice('x😀0',1,3))
        self.assertEqual('',source_slice('😀',2,2))
        for args in [('😀',1,1),('😀',0,1),('😀',1,2),('abc',-1,2),('abc',3,2),('abc',0,4),('abc',False,1),(None,0,1),('abc','0',1),('\ud800',0,1)]:
            with self.assertRaises(ValueError):source_slice(*args)


if __name__=='__main__':unittest.main()
