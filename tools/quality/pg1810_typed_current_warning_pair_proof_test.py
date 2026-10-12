"""All actual primitive bindings, not integer-only source search."""
import ast
import unittest
from pg1810_typed_current_warning_pair_proof import payload


class Typed(unittest.TestCase):
    def test_whole_actual_bound_payload(self):
        raw=payload();tree=ast.parse(raw);values=[n.value for n in ast.walk(tree)if isinstance(n,ast.Constant)]
        for old in [476085,476087,476116,476114,8492401,8492565]:
            self.assertFalse(any(v==old or v==str(old)for v in values if type(v)in(int,str)))
        self.assertTrue(b'PG1800_FRAME method=verify_pid1 line=20'in values)
        self.assertFalse(b'PG1800_FRAME method=capture_data line=58'in values)
        self.assertTrue('4148e3e8-f107-431a-ab27-d6e6d1f1772e'in raw)
        self.assertFalse('f1800e'in raw)
        self.assertFalse('pg1809-current-warning-pair-proof-v1'in raw)
        self.assertFalse('signal.SIGTERM'in raw)


if __name__=='__main__':unittest.main()
