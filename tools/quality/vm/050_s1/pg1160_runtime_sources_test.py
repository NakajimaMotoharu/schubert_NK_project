import ast
import unittest
from pg1160_runtime_sources import files,BASE,HASH


class RuntimeSourceTest(unittest.TestCase):
    def test_current_same_active_and_live_call_closure(self):
        v=files();j=v['Pg1160RuntimeResume.java'];s=v['pg1160_runtime_refs.py'];tree=ast.parse(s)
        for part in [BASE,HASH,'pg1160-runtime-resume-v1','runtime.owned_prepare(','daemon-reload','runtime_tree()','manager.UnrefUnit(u)','bus.close()']:
            self.assertTrue(part in s,part)
        for part in ['Pg1160RuntimeResume','refs.check("prepare")','343a5a1b-d064-47d5-88c2-31c36d7ba7a4','db.rollback();db.close()','root.close()']:
            self.assertTrue(part in j,part)
        self.assertFalse('NativeRoleDirectory'in j);self.assertFalse('systemctl start'in s)
        defs={n.name for n in tree.body if isinstance(n,ast.FunctionDef)}
        for name in ['all_terminal','cohort','values','runtime_configuration','require_runtime_configuration','runtime_tree','require_runtime_tree']:
            self.assertIn(name,defs)
        calls={n.func.id for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)}
        self.assertNotIn('canonical_invalid',calls)
        self.assertNotIn('namespace_failure_proof',calls)


if __name__=='__main__':unittest.main()
