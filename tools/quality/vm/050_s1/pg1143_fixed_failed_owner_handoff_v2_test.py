import ast
import unittest
from pg1143_fixed_failed_owner_handoff_v2 import payload


class NamespaceTest(unittest.TestCase):
    def test_original_before_is_stored_once_observations_separate(self):
        text=payload();tree=ast.parse(text);stores=[]
        def walk(node):
            if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef,ast.Lambda)):return
            if isinstance(node,ast.Name)and isinstance(node.ctx,ast.Store)and node.id=='before':stores.append(node.lineno)
            for child in ast.iter_child_nodes(node):walk(child)
        walk(tree);self.assertEqual(len(stores),1)
        self.assertTrue('owned_snapshot=whole();require(owned_snapshot==PROVEN==whole())'in text)
        self.assertTrue('json.dump(owned_snapshot,f,sort_keys=True)'in text)
        self.assertFalse('before=whole()'in text)
        self.assertTrue('fixed-failed-owner-handoff-v2'in text)
        self.assertLess(text.index('contract.terminate_once(404614'),text.index('contract.terminate_once(404585'))


if __name__=='__main__':unittest.main()
