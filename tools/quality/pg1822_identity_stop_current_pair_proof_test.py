"""Actual all-typed current bind and independent saved-before join."""
import ast
import unittest
from pg1822_identity_stop_current_pair_proof import payload


class Current(unittest.TestCase):
    def test_actual_new_profile_and_retained_before(self):
        raw=payload();tree=ast.parse(raw);values=[n.value for n in ast.walk(tree)if isinstance(n,ast.Constant)]
        for v in [479190,479219,479188,8906867,8907026]:self.assertFalse(v in values or str(v)in values)
        self.assertTrue('4148e3e8-f107-431a-ab27-d6e6d1f1772e'in raw)
        self.assertTrue(b'PG1808_FRAME method=main line=111'in values)
        self.assertTrue("captured['units']==current['units']"in raw)
        self.assertTrue('retainedBeforeSha256'in raw)
        self.assertFalse('signal.SIGTERM'in raw)


if __name__=='__main__':unittest.main()
