"""Independent no-republication protocol, authority suffix and global checks."""
import ast
import builtins
import symtable
import unittest
from pg1100_linked_preservation_sources import files


class Preserve(unittest.TestCase):
    def test_only_fixed_link_move_and_full_original_checks(self):
        v=files();self.assertEqual({'Pg1100LinkedPreservation.java','Pg1100LinkedPreservationTest.java','pg1100_linked_refs.py'},set(v))
        j=v['Pg1100LinkedPreservation.java'];p=v['pg1100_linked_refs.py']
        self.assertTrue('"preserve".equals(args[0])'in j)
        self.assertTrue('refs.check("preserve")'in j)
        self.assertFalse('permits.invalidate('in j);self.assertFalse('Files.move('in j)
        self.assertTrue('pg1094-cold-activate-v1/old-approval.private'in j)
        self.assertTrue('pg1100-linked-preservation-v1'in j)
        t=ast.parse(p);attrs={n.attr for n in ast.walk(t)if isinstance(n,ast.Attribute)}
        self.assertNotIn('exchange',attrs);self.assertNotIn('symlink',attrs)
        renames=[n for n in ast.walk(t)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=='rename']
        self.assertEqual(1,len(renames));self.assertEqual('pg1088-current.part',ast.literal_eval(renames[0].args[0]));self.assertEqual('current-link.private',ast.literal_eval(renames[0].args[1]))
        self.assertTrue("[b'Pg1100LinkedPreservation',b'preserve',b'']"in p)
        self.assertTrue('pub.verify_retained'in p)
        self.assertTrue('partial.partial'in p)

    def test_entrypath_globals_and_all_helpers_are_single_bound_definitions(self):
        p=files()['pg1100_linked_refs.py'];t=symtable.symtable(p,'linked-preserver','exec')
        bound={a.get_name()for a in t.get_symbols()if a.is_assigned()or a.is_imported()or a.is_namespace()};missing=set()
        def walk(scope):
            for a in scope.get_symbols():
                if a.is_global()and a.is_referenced()and a.get_name()not in bound and not hasattr(builtins,a.get_name()):missing.add(a.get_name())
            for child in scope.get_children():walk(child)
        walk(t);self.assertEqual(set(),missing)
        definitions=[n.name for n in ast.parse(p).body if isinstance(n,ast.FunctionDef)]
        self.assertEqual(len(definitions),len(set(definitions)))


if __name__=='__main__':unittest.main()
