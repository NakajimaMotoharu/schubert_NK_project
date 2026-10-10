import ast
import unittest
from pg1157_native_failed_owner_handoff import payload


class HandoffTest(unittest.TestCase):
    def test_exact_owner_child_first_once_and_no_original_overwrite(self):
        s=payload();tree=ast.parse(s)
        self.assertTrue('terminate_once(410308,4653520'in s)
        self.assertTrue('terminate_once(410279,4653404'in s)
        self.assertLess(s.index('terminate_once(410308'),s.index('terminate_once(410279'))
        self.assertTrue('owned_snapshot==PROVEN==whole()'in s)
        self.assertTrue("'oldOperationNormalClose':False"in s)
        self.assertFalse('systemctl stop'in s)
        def count(n,name):
            if isinstance(n,(ast.FunctionDef,ast.ClassDef,ast.Lambda)):return 0
            return int(isinstance(n,ast.Name)and isinstance(n.ctx,ast.Store)and n.id==name)+sum(count(c,name)for c in ast.iter_child_nodes(n))
        for name in ['before','FILES','NATIVE_FILES','CURRENT','PROVEN']:self.assertEqual(count(tree,name),1,name)


if __name__=='__main__':unittest.main()
