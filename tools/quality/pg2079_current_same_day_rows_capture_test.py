"""Actual full generated source, pinned before-image and distinct qualified terminal input."""
import unittest
from pg2079_current_same_day_rows_capture import payload,entry,SLOT


class Capture(unittest.TestCase):
    def test_actual_current_literal_source_roles(self):
        raw=payload()
        for marker in ['796965f389b631bf8abb49f6cbccf88955fbf3afe39edec0194316df35248a05','a31dd6da-cf4c-4d0f-ab7c-5c8bb59c0b75','2026-10-13T03:08:18.452473Z','classify_inbox','read only','_selectors']:
            self.assertTrue(marker in raw,marker)
        self.assertEqual(SLOT,entry().__globals__['SLOT'])


if __name__=='__main__':unittest.main()
