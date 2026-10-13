"""Real emitted read scopes: no fixture adds attributes or changes expectations."""
import ast
import unittest
from pg1963_reload_ref_scoped_full_post import payload
from pg1960_closed_configuration_ref_diagnosis import payload as diagnosis


class Scope(unittest.TestCase):
    def test_full_post_qualification_inside_complete_ref_scope(self):
        tree=ast.parse(payload());scope=next(n for n in tree.body if isinstance(n,ast.Try)and any(isinstance(x,ast.FunctionDef)and x.name=='snapshot'for x in n.body))
        qualification=next(n for n in scope.body if isinstance(n,ast.For)and any(isinstance(x,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='actual'for t in x.targets)for x in n.body))
        ref_loop=next(n for n in scope.body if isinstance(n,ast.For)and any(isinstance(c,ast.Call)and isinstance(c.func,ast.Attribute)and c.func.attr=='RefUnit'for c in ast.walk(n)))
        self.assertLess(ref_loop.lineno,qualification.lineno)
        self.assertTrue(any(isinstance(c,ast.Call)and isinstance(c.func,ast.Attribute)and c.func.attr=='UnrefUnit'for n in scope.finalbody for c in ast.walk(n)))
        self.assertTrue(any(isinstance(c,ast.Call)and isinstance(c.func,ast.Attribute)and c.func.attr=='close'for n in scope.finalbody for c in ast.walk(n)))
        self.assertIn('SuccessExitStatus=10',payload());self.assertIn('oldReloadToolCloseUnknownRetained',payload())

    def test_diagnosis_owns_refs_before_reads_and_releases_normally(self):
        tree=ast.parse(diagnosis());scope=next(n for n in tree.body if isinstance(n,ast.Try))
        self.assertIn('RefUnit',ast.unparse(scope.body[0]))
        self.assertIn('UnrefUnit',ast.unparse(scope.finalbody[0]));self.assertIn('bus.close()',ast.unparse(scope.finalbody[-1]))


if __name__=='__main__':unittest.main()
