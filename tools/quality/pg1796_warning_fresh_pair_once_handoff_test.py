"""Fresh proof/phase globals/SAVE, manager exact, ordinary peer socket bindings."""
import ast
import unittest
from pg1796_warning_fresh_pair_once_handoff import payload,SLOT


class Once(unittest.TestCase):
    def test_actual_composed_all_namespaces_and_typed_guards(self):
        raw=payload();tree=ast.parse(raw)
        save=[n for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='SAVE'for t in n.targets)][-1]
        self.assertEqual("SAVE = BASE / '"+SLOT+"'",ast.unparse(save))
        self.assertTrue("pg1794-warning-fresh-pair-readonly-v1/proof.private.json" in raw)
        self.assertFalse('pg1788-warning-pair-once-handoff-v3' in raw)
        original=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='original')
        self.assertEqual("def original():\n    require(capture() == retained_proof['fullCurrent'])",ast.unparse(original))
        self.assertTrue("match_parent_history(retained_proof['parent'],parent)" in raw)
        self.assertTrue("match_peer_history(retained_proof['peer'],same_peer())" in raw)
        self.assertFalse('signal.SIGKILL' in raw)
        self.assertTrue("owner={'schubert_app':451130,'schubert_web_session':452144}" in raw)


if __name__=='__main__':unittest.main()
