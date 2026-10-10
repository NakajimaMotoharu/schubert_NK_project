"""Fixed profile and complete pre/post proof for the qualified once-tree primitive."""
import ast
import builtins
import symtable
import unittest
from pg1099_partial_exchange_handoff import payload


class Handoff(unittest.TestCase):
    def test_exact_once_generations_and_whole_partial_post_without_publication(self):
        s=payload();tree=ast.parse(s)
        calls=[n for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=='once_tree']
        self.assertEqual(1,len(calls));self.assertEqual((16222,3020295),ast.literal_eval(calls[0].args[0]));self.assertEqual((16248,3020358),ast.literal_eval(calls[0].args[1]))
        self.assertIn("'partialTrees': partial_state()",s)
        self.assertIn("'runtime': runtime()",s)
        self.assertIn('proof.capture()',s)
        attributes={n.attr for n in ast.walk(tree)if isinstance(n,ast.Attribute)}
        self.assertIn('SIGTERM',attributes);self.assertNotIn('SIGKILL',attributes)
        self.assertIn("'oldOperationNormalClose': False",s)
        self.assertIn('NameHasOwner(CHILD_BUS)',s)
        self.assertNotIn('os.rename(',s);self.assertNotIn('os.symlink(',s)
        self.assertNotIn('permits.invalidate(',s)

    def test_bound_globals_and_no_old_generation_in_runtime_ast(self):
        s=payload();t=symtable.symtable(s,'fixed-handoff','exec')
        bound={a.get_name()for a in t.get_symbols()if a.is_assigned()or a.is_imported()or a.is_namespace()};missing=set()
        def walk(scope):
            for a in scope.get_symbols():
                if a.is_global()and a.is_referenced()and a.get_name()not in bound and not hasattr(builtins,a.get_name()):missing.add(a.get_name())
            for child in scope.get_children():walk(child)
        walk(t);self.assertEqual(set(),missing)
        integers={n.value for n in ast.walk(ast.parse(s))if isinstance(n,ast.Constant)and type(n.value)is int}
        self.assertNotIn(5463,integers);self.assertNotIn(5489,integers)


if __name__=='__main__':unittest.main()
