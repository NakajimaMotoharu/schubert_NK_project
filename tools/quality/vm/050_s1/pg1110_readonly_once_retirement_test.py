"""Independent fixed-only once pidfd and whole pre/post source qualification."""
import ast
import builtins
import symtable
import unittest
from pg1110_readonly_once_retirement import payload


class Retirement(unittest.TestCase):
    def test_fixed_readonly_actor_once_reservation_and_no_start(self):
        s=payload();tree=ast.parse(s)
        calls=[n for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=='terminate_once']
        self.assertEqual(1,len(calls));self.assertEqual(20312,ast.literal_eval(calls[0].args[0]));self.assertEqual(3250518,ast.literal_eval(calls[0].args[1]))
        self.assertTrue("'oldNormalClose':False"in s)
        self.assertTrue('external-start-guard.private.json'in s)
        self.assertTrue('assert after==before[\'post\']==post()'in s)
        attrs={n.attr for n in ast.walk(tree)if isinstance(n,ast.Attribute)}
        self.assertNotIn('StartUnit',attrs);self.assertNotIn('SIGKILL',attrs)
        self.assertIn('SIGTERM',attrs);self.assertIn('durable_reservation',attrs)

    def test_global_bindings_and_actual_source_error_witness(self):
        s=payload();t=symtable.symtable(s,'readonly-retirement','exec');names={a.get_name()for a in t.get_symbols()if a.is_assigned()or a.is_imported()or a.is_namespace()};missing=set()
        def walk(scope):
            for a in scope.get_symbols():
                if a.is_global()and a.is_referenced()and a.get_name()not in names and not hasattr(builtins,a.get_name()):missing.add(a.get_name())
            for child in scope.get_children():walk(child)
        walk(t);self.assertEqual(set(),missing)


if __name__=='__main__':unittest.main()
