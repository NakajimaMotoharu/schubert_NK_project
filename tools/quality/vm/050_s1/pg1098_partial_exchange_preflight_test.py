"""Independent frozen actor/partial/source and entrypath global qualification."""
import ast
import builtins
import symtable
import unittest
from pg1098_partial_exchange_preflight import payload


class Preflight(unittest.TestCase):
    def test_fixed_profiles_no_publication_or_signals_and_complete_unlinked_original(self):
        code=payload()
        self.assertIn('actor(16222,3020295,PARENT_ARGV',code)
        self.assertIn('actor(16248,3020358,CHILD_ARGV',code)
        self.assertIn('original_row,io.fd_record(old_approval_fd)',code)
        self.assertIn('partial.partial(original_before',code)
        self.assertIn('sameReadOnlyPeerSocket',code)
        self.assertNotIn('pidfd_send_signal',code)
        self.assertNotIn('os.rename(',code)
        self.assertNotIn('os.symlink(',code)
        self.assertNotIn('permits.invalidate(',code)
        self.assertIn('manager.RefUnit(name)',code)
        self.assertIn('manager.UnrefUnit(name)',code)

    def test_all_generated_entrypath_globals_are_bound(self):
        code=payload();t=symtable.symtable(code,'fixed-partial-observer','exec')
        names={s.get_name()for s in t.get_symbols()if s.is_imported()or s.is_assigned()or s.is_namespace()}
        missing=set()
        def walk(scope):
            for s in scope.get_symbols():
                if s.is_global()and s.is_referenced()and s.get_name()not in names and not hasattr(builtins,s.get_name()):missing.add(s.get_name())
            for child in scope.get_children():walk(child)
        walk(t);self.assertEqual(set(),missing)
        ast.parse(code)


if __name__=='__main__':unittest.main()
