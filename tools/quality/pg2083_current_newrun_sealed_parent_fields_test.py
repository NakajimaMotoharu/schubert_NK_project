"""Fixed public schema/readOnly source and strict qualified hash boundary."""
import unittest
from pyflakes.api import check
from pg2083_current_newrun_sealed_parent_fields import payload


class Projection(unittest.TestCase):
    def test_hash_and_whole_public_projection(self):
        raw=payload('a'*64);self.assertEqual(0,check(raw,'<actual public current projection>'))
        self.assertTrue("len(fields)==18"in raw)
        for bad in [None,'','A'*64,'a'*63,'g'*64]:
            with self.assertRaises(ValueError):payload(bad)


if __name__=='__main__':unittest.main()
