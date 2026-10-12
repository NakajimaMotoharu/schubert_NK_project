"""Actual fresh namespace/immutable reference and typed boundary joins."""
import ast
import unittest
from pg1794_warning_fresh_pair_proof import payload,SLOT


class Fresh(unittest.TestCase):
    def test_actual_payload_retains_oldproof_and_fresh_shared_contract(self):
        raw=payload();tree=ast.parse(raw)
        save=[n for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='SAVE'for t in n.targets)][-1]
        self.assertEqual("SAVE = BASE / '"+SLOT+"'",ast.unparse(save))
        self.assertTrue("history_raw=(BASE/'pg1782-warning-live-peer-readonly-v1/proof.private.json').read_bytes()" in raw)
        self.assertTrue("match_parent_history(history['parent'],parent)" in raw)
        self.assertTrue("match_peer_history(history['peer'],peer)" in raw)
        self.assertFalse('pidfd_send_signal' in raw)


if __name__=='__main__':unittest.main()
