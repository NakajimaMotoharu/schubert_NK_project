import ast
import unittest
from pyflakes.api import check,checkPath
import pg5434_current_full_preservation as entry


class FreshPreservation(unittest.TestCase):
    def test_exact_immutable_previous_reader_changes_only_one_output_name(self):
        old=entry.previous.payload();new=entry.payload()
        self.assertEqual(new.replace("save = base / "+repr(entry.SLOT),"save = base / "+repr(entry.previous.SLOT),1),old)
        self.assertEqual(check(new,'<complete readonly full11>'),0)
        self.assertIn('repeatable read read only',new)
        tree=ast.parse(new)
        self.assertFalse(any(isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr in ('unlink','rename','rmdir') for node in ast.walk(tree)))
        for path in (entry.__file__,__file__):self.assertEqual(checkPath(path),0)


if __name__=='__main__':unittest.main()
