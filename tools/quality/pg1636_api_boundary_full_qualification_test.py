"""Literal module counts and class scope of the actual generated verifier."""
import ast
import unittest
import pg1636_api_boundary_full_qualification as p


class FullSourceQualifierTest(unittest.TestCase):
    def test_exact_independent_module_totals_and_no_old_exec_inputs(self):
        raw=p.server();tree=ast.parse(raw)
        expected=ast.literal_eval(next(n.value for n in tree.body if isinstance(n,ast.Assign)and isinstance(n.targets[0],ast.Name)and n.targets[0].id=='expected'))
        self.assertEqual({'protocol':(81,17,174),'storage':(163,23,74),'bootstrap':(298,40,105),'api':(968,159,407),'web':(886,129,315),'batch':(1200,164,568)},expected)
        self.assertEqual((3596,532,1643),tuple(sum(v[i]for v in expected.values())for i in range(3)))
        self.assertIn("B/'runs/PG1532-six-v1/manifest.safe.json'",raw)
        self.assertIn("S=B/'source-full-PG1633'",raw)
        self.assertIn('ApiTerminalCapture',raw);self.assertIn('ApiProcessLifetime$1.class',raw)
        self.assertIn("'formalAccepted':False",raw)
        self.assertNotIn('ExecFileLoader',raw)


if __name__=='__main__':unittest.main()
