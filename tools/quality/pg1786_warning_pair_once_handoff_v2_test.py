"""AST actual namespace golden; no old proof mutation or old signal slot."""
import ast
import unittest
from pg1786_warning_pair_once_handoff_v2 import payload,SLOT


class Namespace(unittest.TestCase):
    def test_real_top_level_writable_namespace_is_not_immutable_proof(self):
        raw=payload();tree=ast.parse(raw)
        saves=[ast.unparse(n)for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='SAVE'for t in n.targets)]
        self.assertEqual("SAVE = BASE / '"+SLOT+"'",saves[-1])
        handoff=next(n for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='HANDOFF'for t in n.targets))
        self.assertEqual("HANDOFF = BASE / '"+SLOT+"'",ast.unparse(handoff))
        self.assertFalse('pg1784-warning-pair-once-handoff-v1' in raw)
        self.assertTrue("BASE/'pg1782-warning-live-peer-readonly-v1/proof.private.json'" in raw)
        self.assertTrue('4c226a4e958291f100b1b20e05ff854dda3e511e1cdc58d16cb11bfb85834a6d' in raw)
        self.assertLess(raw.index('require(not os.path.lexists(SAVE))'),raw.index('HANDOFF.mkdir(mode=0o700)'))


if __name__=='__main__':unittest.main()
