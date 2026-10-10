import ast
import unittest
from pg1281_current_readonly_guard import payload


class CurrentGuardTest(unittest.TestCase):
    def test_no_business_write_and_reference_lifetime_retained(self):
        code = payload()
        tree = ast.parse(code)
        self.assertIn('PG1281-current-readonly-v1', code)
        self.assertNotIn("save=base/'", code)
        self.assertNotIn(".mkdir(", code)
        scope = next(n for n in tree.body if isinstance(n, ast.Try))
        self.assertTrue(scope.finalbody)
        self.assertIn('UnrefUnit', ast.unparse(scope))
        self.assertIn('native = snapshot()', ast.unparse(scope))
        self.assertIn('require(native == snapshot())', ast.unparse(scope))
        self.assertNotIn('StartUnit', code)
        self.assertNotIn('StopUnit', code)


if __name__ == '__main__':
    unittest.main()
