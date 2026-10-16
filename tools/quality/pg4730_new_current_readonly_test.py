"""Actual new source and full11 binding, no old failed summary or active authority."""
import ast
import unittest
from pyflakes.api import check,checkPath
import pg4730_new_current_readonly as tool


class NewCurrent(unittest.TestCase):
    def test_source_bom_current_full11_capacity_and_normal_close(self):
        raw=tool.payload()
        self.assertEqual(0,check(raw,'<current full reader>'))
        for value in [tool.SOURCE,tool.BOM,tool.AFTER,tool.AFTER_SHA,'12884901888','complete_configuration',"==64)"]:
            self.assertIn(value,raw)
        self.assertNotIn('parentExit',raw);self.assertNotIn('systemctl\',\'start',raw)
        t=ast.parse(raw)
        owned=next(n for n in t.body if isinstance(n,ast.Try)and 'UnrefUnit'in ast.unparse(n.finalbody))
        output=next(n for n in t.body if isinstance(n,ast.Expr)and isinstance(n.value,ast.Call)and ast.unparse(n.value.func)=='print')
        self.assertGreater(output.lineno,owned.end_lineno)
        self.assertEqual(0,checkPath(tool.__file__));self.assertEqual(0,checkPath(__file__))


if __name__=='__main__':unittest.main()
