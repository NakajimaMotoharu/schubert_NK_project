"""Literal current pair bindings and pure FD rejection; no VM operation."""
import ast
import unittest
import pg2138_current_normal_pair_proof as p


class PairTests(unittest.TestCase):
    def test_whole_payload_fixed_roles_and_no_signal(self):
        raw = p.payload(); tree = ast.parse(raw)
        constants = [n.value for n in ast.walk(tree) if isinstance(n, ast.Constant)]
        for value in [676884,12181426,676916,12181630,676914]:
            self.assertIn(value, constants)
        for value in [289328,291213,291242,291240,5627480,5962938]:
            self.assertNotIn(value, constants)
        self.assertIn('SuccessExitStatus', raw)
        self.assertIn('normalUnit0or10', raw)
        self.assertIn("lines[-2:] == [b'1', b'1']", raw)
        self.assertIn('candidateNotPlaced', raw)
        self.assertNotIn('pidfd_send_signal', raw)
        self.assertNotIn('pg_terminate_backend', raw)
        self.assertNotIn('systemctl start', raw)

    def test_literal_fd_relations_and_negative(self):
        tree=ast.parse(p.helpers())
        node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='fd_relation')
        ns={};exec(compile(ast.Module(body=[node],type_ignores=[]),'<pure literal FD oracle>','exec'),ns)
        fn=ns['fd_relation']
        got=fn('maintenance.lock',['88','91','92'],['92'],lambda a,b:1)
        self.assertEqual([(x['a'],x['b'],x['sameOfd'])for x in got],[('88','91',False),('88','92',False),('91','92',False)])
        self.assertEqual(fn('startup-admission.lock',['101','128'],['101','128'],lambda a,b:0),[{'a':'101','b':'128','sameOfd':True}])
        for name,linked,locking,compare in [('foreign',[],[],lambda a,b:0),('maintenance.lock',['30','33','34'],['34'],lambda a,b:1),('maintenance.lock',['88','91','92'],['92'],lambda a,b:0),('startup-admission.lock',['101','128'],['101','128'],lambda a,b:1),('startup-admission.lock',['101','128'],['101','128'],lambda a,b:-1),('startup-admission.lock',['101','128'],['101','128'],lambda a,b:None)]:
            with self.assertRaises(ValueError):fn(name,linked,locking,compare)


if __name__=='__main__':unittest.main()
