"""Actual composed namespaces and all original authority IDs remain fixed."""
import ast
import unittest
from pg1809_current_warning_pair_proof import payload


class Actual(unittest.TestCase):
    def test_payload_current_actor_not_uuid_rewrite(self):
        raw=payload();tree=ast.parse(raw)
        values=[n.value for n in ast.walk(tree)if isinstance(n,ast.Constant)]
        self.assertTrue('4148e3e8-f107-431a-ab27-d6e6d1f1772e'in raw)
        self.assertFalse('f1800e'in raw)
        self.assertFalse(any(v in [476087,476116,476114,8492401,8492565]for v in values if type(v)is int))
        self.assertTrue(479190 in values);self.assertTrue(479219 in values)
        self.assertTrue('pg1800-warning-owned-stop-tools-v1'in raw)
        self.assertTrue('PG1800_FRAME method=verify_pid1 line=20'in raw)
        self.assertFalse('signal.SIGTERM'in raw)


if __name__=='__main__':unittest.main()
