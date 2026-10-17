"""Same actual whole functions, current source/hash, no start or credentials."""
import ast
import unittest
from pyflakes.api import check,checkPath
import pg4930_current_bootstrap_before as target


class CurrentBefore(unittest.TestCase):
    def test_current_full_functions_unmodified_and_readonly(self):
        raw=target.payload();old=(target.admission.W/target.post.SLOT/'payload.private.py').read_text()
        functions=lambda text:{n.name:ast.dump(n,include_attributes=False)for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)}
        prior,current=functions(old),functions(raw)
        self.assertTrue(set(prior)<=set(current))
        for name,body in prior.items():self.assertEqual(body,current[name],name)
        for value in (target.SOURCE,target.BOM,target.AFTER,target.SLOT):self.assertIn(value,raw)
        for value in (target.previous.SOURCE,target.previous.SLOT,"save=base/'pg4922-current-owned-post-v1'",'StartUnit','StopUnit','reset-failed','daemon-reload'):
            self.assertNotIn(value,raw)
        self.assertEqual(0,check(raw,'<all current stopped before globals>'))
        self.assertEqual(0,checkPath(target.__file__));self.assertEqual(0,checkPath(__file__))

    def test_enrichment_in_tenref_scope_without_credential_mutation(self):
        tree=ast.parse(target.payload());scope=next(n for n in tree.body if isinstance(n,ast.Try)and n.finalbody)
        body=ast.unparse(ast.Module(body=scope.body,type_ignores=[]));final=ast.unparse(ast.Module(body=scope.finalbody,type_ignores=[]))
        for value in ("users[0]['role'] == 'ADMIN'",'bootstrap-admin-username','bootstrap-admin-password','dependency_graph',"'native': native",'os.fsync'):self.assertIn(value,body)
        self.assertIn('UnrefUnit',final);self.assertIn('bus.close()',final)


if __name__=='__main__':unittest.main()
