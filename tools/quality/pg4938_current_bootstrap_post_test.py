"""Actual current execute receipt is required; captured20 precedes GC/all-resource checks."""
import ast
import unittest
from pyflakes.api import check,checkPath
import pg4938_current_bootstrap_post as role


class IndependentPost(unittest.TestCase):
    def test_current_actual20_independent_post_namespace_and_order(self):
        raw=role.payload();self.assertEqual(0,check(raw,'<actual current captured20 post>'))
        for text in (role.role.SOURCE,role.role.BOM,role.role.BASELINE,role.role.before.SLOT,
                     "boot_before['rows']==boot_after['rows']==after['rows']",
                     "CONTRACT['same_terminal_cohort']","CONTRACT['native_tree']",
                     "save=base/'pg4938-current-bootstrap-post-v1'","'allResources0':True"):
            self.assertIn(text,raw)
        self.assertLess(raw.index("terminal=boot_after['units'][bootstrap]"),raw.index('current_bootstrap=show'))
        self.assertLess(raw.index('refs.append(u)'),raw.index('current_bootstrap=show'))
        for old in ('pg4820','pg4818','PG4702','fff841d9-2554','systemctl start','reset-failed','pg1727-bootstrap-recovery'):
            self.assertNotIn(old,raw)
        self.assertEqual(0,checkPath(role.__file__));self.assertEqual(0,checkPath(__file__))

    def test_all_current_before_functions_preserved(self):
        raw=role.payload();before=(role.role.W/role.role.before.SLOT/'payload.private.py').read_text()
        functions=lambda text:{n.name:ast.dump(n,include_attributes=False)for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)}
        original,current=functions(before),functions(raw)
        for name,body in original.items():self.assertEqual(body,current[name],name)


if __name__=='__main__':unittest.main()
