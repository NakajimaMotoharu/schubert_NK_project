"""Actual post does not call producer contract; exact literal and original-zero checks."""
import ast
import unittest
from pyflakes.api import check
from pg1986_fresh_resume_independent_post import payload


class Post(unittest.TestCase):
    def test_independent_actual_scope_and_closed_full_oracle(self):
        raw=payload();self.assertEqual(0,check(raw,'<actual independent post>'))
        self.assertNotIn('resume_contract',raw);self.assertNotIn('fixed_dropin(',raw)
        self.assertIn('right[:3]==(left[0]',raw);self.assertIn('zz-pg1980-once-resume.conf',raw)
        self.assertIn('runtime_actual==json.loads',raw);self.assertIn('oldReloadToolCloseUnknownRetained',raw)
        self.assertIn("lines[-2:] == [b'0', b'0']",raw)
        tree=ast.parse(raw);scope=next(n for n in tree.body if isinstance(n,ast.Try)and any(isinstance(x,ast.FunctionDef)and x.name=='snapshot'for x in n.body))
        names=ast.unparse(scope)
        self.assertLess(names.index('manager.RefUnit'),names.index('fresh_private'))
        self.assertIn('manager.UnrefUnit',ast.unparse(scope.finalbody[0]));self.assertIn('bus.close()',names)


if __name__=='__main__':unittest.main()
