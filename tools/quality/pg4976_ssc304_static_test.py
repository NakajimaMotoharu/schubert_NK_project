"""Complete fixed namespace and no duplicated analyzer / lost numeric exit regression."""
import ast
import unittest
from pyflakes.api import check,checkPath
import pg4976_ssc304_static as role


class StaticDiagnostic(unittest.TestCase):
    def test_single_phase_and_numeric_exit_before_following_checks(self):
        data={'includeCheckstyle':False,'staticJob':'PG4976-ssc304-static-v1','source':role.SOURCE}
        raw=role.server_source(data)
        self.assertEqual(0,check(raw,'<complete current diagnostic namespace>'));ast.parse(raw)
        self.assertLess(raw.index("with(out/'pmd-exit.safe.json')"),raw.index("root=E.parse(out/'pmd.xml')"))
        self.assertLess(raw.index("with(out/'checkstyle-exit.safe.json')"),raw.index("errors = E.parse(out / 'checkstyle.xml')"))
        self.assertEqual(1,raw.count('r=subprocess.run(argv,'));self.assertEqual(1,raw.count('checked = subprocess.run(argv,'))
        self.assertIn('source-full-PG4968',raw);self.assertNotIn('source-full-PG4844',raw)
        self.assertIn('runs/PG4856-static-completion-v1',raw);self.assertIn("'F03Accepted':False",raw)
        with self.assertRaises(ValueError):role.server_source({**data,'includeCheckstyle':True})
        for p in(role.__file__,__file__):self.assertEqual(0,checkPath(p))


if __name__=='__main__':unittest.main()
