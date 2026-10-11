"""Actual full payload order, metadata shape and public/file identity."""
import ast
import unittest
import pg1361_bootstrap_fixed_pair_handoff as p

class Test(unittest.TestCase):
    def test_fixed_pair_guard_and_once_order(self):
        raw=p.payload(dict.fromkeys(p.proof.previous.previous.prior.prior.previous.transport.previous.SEALS,'b'*64))
        tree=ast.parse(raw)
        functions={n.name:ast.get_source_segment(raw,n) for n in tree.body if isinstance(n,ast.FunctionDef)}
        self.assertTrue('Pg1356BootstrapExisting' in functions['candidate'])
        self.assertTrue("locks[name]=list(metadata9(st))" in functions['fixed_owner'])
        self.assertTrue("'child':None" in functions['parent_only'])
        self.assertFalse('len(kids)==1' in functions['parent_only'])
        self.assertTrue(raw.index('terminate_once(839655,7753240')<raw.index('terminate_once(839626,7753101'))
        self.assertTrue('signals==2' in raw)
        self.assertTrue('PG1361-bootstrap-fixed-pair-handoff-v1' in raw)
        self.assertTrue('pg1361-bootstrap-fixed-pair-handoff-v1' in raw)
        self.assertFalse('PG1353_RECOVERY' in raw)
        self.assertTrue('oldNormalClose' in raw)
        self.assertTrue(p.PROOF in raw)

if __name__=='__main__':
    unittest.main()
