"""Actual current pair/source/before guards, UUID identity and one-shot sequence."""
import ast
import unittest
from pg1823_identity_stop_pair_once_handoff import payload,SLOT


class Current(unittest.TestCase):
    def test_current_namespace_and_first_before_history(self):
        raw=payload();tree=ast.parse(raw)
        saves=[n for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id in ['SAVE','HANDOFF']for t in n.targets)]
        for n in saves[-2:]:self.assertTrue(SLOT in ast.unparse(n))
        self.assertTrue('pg1822-identity-stop-current-pair-proof-v1/proof.private.json'in raw)
        self.assertTrue('terminate(481540, 9066872, before_child)'in raw)
        self.assertTrue('terminate(481511, 9066715, parent_after_child)'in raw)
        self.assertTrue('4148e3e8-f107-431a-ab27-d6e6d1f1772e'in raw)
        self.assertFalse('signal.SIGKILL'in raw)
        self.assertTrue('parent_image_after_child() if CHILD_REAPED else recovery_actor()'in raw)


if __name__=='__main__':unittest.main()
