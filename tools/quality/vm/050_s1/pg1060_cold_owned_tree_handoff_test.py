"""PT-DEP-1060001..002 exact fixed tree/pinned preflight and zero-peer post wiring."""
import ast
import unittest
from pg1060_cold_owned_tree_handoff import payload


class OwnedTree(unittest.TestCase):
    def test_fixed_pair_once_with_whole_reservation_and_post(self):
        raw=payload();tree=ast.parse(raw)
        self.assertIn('tree_contract.once_tree((5463, 1373880), (5489, 1373951)',raw)
        self.assertIn('assert v == qualified',raw)
        self.assertIn("'proofSha256': hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()",raw)
        self.assertIn('assert v == expected',raw)
        self.assertIn('contract.free_flocks(lines, m)',raw)
        self.assertIn("env['OWNER_BACKEND'] = 0",raw)
        self.assertNotIn('SIGKILL',raw);self.assertNotIn('pg_terminate_backend',raw)
        self.assertEqual(1,sum(isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=='pidfd_send_signal'for n in ast.walk(tree)))

    def test_original_child_identity_not_new_orphan_and_bus_exit_unknown(self):
        raw=payload()
        self.assertIn("assert child == before['tree']['child']",raw)
        self.assertIn("set(), 1)",raw)
        self.assertIn('not daemon.NameHasOwner(CHILD_BUS)',raw)
        self.assertIn("'oldOperationNormalClose': False",raw)
        self.assertIn("'childExitUnknown': True",raw)
        self.assertIn('except BaseException as failure:\n    retained_error(failure)',raw)


if __name__=='__main__':
    unittest.main()
