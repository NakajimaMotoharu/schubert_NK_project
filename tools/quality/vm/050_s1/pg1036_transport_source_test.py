"""No SSH; long-wait completion must retain dispatch source, not current HEAD."""
import ast
import unittest
from pg1025_cold_owned_native import source


class Source(unittest.TestCase):
    def test_start_head_is_unique_and_final_uses_start_record(self):
        raw = source()
        tree = ast.parse(raw)
        head_calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
                      and isinstance(n.func, ast.Attribute) and n.func.attr == 'check_output'
                      and n.args and isinstance(n.args[0], ast.List)
                      and [x.value for x in n.args[0].elts if isinstance(x, ast.Constant)] == ['git','rev-parse','HEAD']]
        self.assertEqual(1,len(head_calls))
        self.assertTrue("'operatorSource':begin_record['operatorSource']" in raw)
        self.assertTrue("with Path(str(base)+'.begin.safe.json').open('x')" in raw)


if __name__ == '__main__': unittest.main()
