"""Full actual stopped verifier retained and enriched baseline inside normal Ref lifetime."""
import ast
import unittest
from pyflakes.api import check,checkPath
import pg4818_new_current_bootstrap_before as target


class BootstrapBefore(unittest.TestCase):
    def test_actual_stopped_readonly_verifier_not_weakened(self):
        raw=target.payload();original=(target.admission.W/target.post.SLOT/'payload.private.py').read_text()
        functions=lambda value:{n.name:ast.dump(n,include_attributes=False)for n in ast.parse(value).body if isinstance(n,ast.FunctionDef)}
        before,after=functions(original),functions(raw)
        self.assertTrue(set(before)<=set(after))
        for name,body in before.items():self.assertEqual(body,after[name],name)
        self.assertIn(target.SOURCE,raw);self.assertIn(target.BOM,raw);self.assertIn(target.AFTER,raw)
        self.assertEqual(0,check(raw,'<actual baseline all globals>'));self.assertEqual(0,checkPath(target.__file__))
        for forbidden in ['StartUnit','StopUnit',"'--no-block'","'daemon-reload'","'pg1718-current-bootstrap-before-v1'"]:self.assertNotIn(forbidden,raw)

    def test_private_enrichment_before_normal_ref_return_and_no_authority(self):
        raw=target.payload();tree=ast.parse(raw)
        scope=next(n for n in tree.body if isinstance(n,ast.Try)and n.finalbody)
        body=ast.unparse(ast.Module(body=scope.body,type_ignores=[]));final=ast.unparse(ast.Module(body=scope.finalbody,type_ignores=[]))
        self.assertIn("users[0]['role'] == 'ADMIN'",body)
        self.assertIn('bootstrap-admin-username',body);self.assertIn('bootstrap-admin-password',body)
        self.assertIn('dependency_graph',body);self.assertIn("'native': native",body)
        self.assertIn('snapshot_raw',body);self.assertIn('os.fsync',body)
        self.assertIn('UnrefUnit',final);self.assertIn('bus.close()',final)
        self.assertIn("'normalNewReferences': True",ast.unparse(tree))
        self.assertEqual(0,checkPath(__file__))


if __name__=='__main__':unittest.main()
