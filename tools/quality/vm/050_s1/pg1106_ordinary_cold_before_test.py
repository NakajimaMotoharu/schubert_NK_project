"""Independent noargs/old-original/budget/current source before qualification."""
import ast
import builtins
import symtable
import unittest
from pg1106_ordinary_cold_before import payload


class Before(unittest.TestCase):
    def test_current_signed_default_and_actual_budget_no_start_or_resume(self):
        s=payload();t=ast.parse(s)
        attrs={n.attr for n in ast.walk(t)if isinstance(n,ast.Attribute)}
        self.assertNotIn('StartUnit',attrs);self.assertNotIn('pidfd_send_signal',attrs)
        self.assertTrue("assert budget==b'30min\\n'"in s)
        self.assertTrue("effective[:3]==('/usr/bin/java',command,'no')"in s)
        self.assertTrue("rootBudgetSeconds=1800"in s)
        self.assertTrue('nativeBeforeEmpty=True'in s)
        self.assertTrue("oldOriginalCompleted=True"in s)
        self.assertTrue("after=ordinary_post();assert after==ordinary_post()"in s)

    def test_entrypath_globals_and_single_active_functions(self):
        s=payload();t=symtable.symtable(s,'ordinary-before','exec')
        bound={a.get_name()for a in t.get_symbols()if a.is_assigned()or a.is_imported()or a.is_namespace()};missing=set()
        def walk(scope):
            for a in scope.get_symbols():
                if a.is_global()and a.is_referenced()and a.get_name()not in bound and not hasattr(builtins,a.get_name()):missing.add(a.get_name())
            for child in scope.get_children():walk(child)
        walk(t);self.assertEqual(set(),missing)
        names=[n.name for n in ast.parse(s).body if isinstance(n,ast.FunctionDef)];self.assertEqual(len(names),len(set(names)))


if __name__=='__main__':unittest.main()
