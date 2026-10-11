"""Full generated candidate/parent/ref/post and public slot identity."""
import ast
import unittest
import pg1368_bootstrap_fixed_ref_handoff as p

class Test(unittest.TestCase):
    def test_actual_fixed_pair_and_held_observer(self):
        raw=p.payload(dict.fromkeys(p.proof.previous.previous.previous.prior.prior.previous.transport.previous.SEALS,'b'*64));tree=ast.parse(raw)
        functions={n.name:ast.get_source_segment(raw,n)for n in tree.body if isinstance(n,ast.FunctionDef)}
        self.assertTrue('Pg1362BootstrapExisting'in functions['candidate'])
        self.assertTrue("'child':None"in functions['parent_only'])
        self.assertTrue("'bus':names"in functions['fixed_owner'])
        self.assertTrue(raw.index('terminate_once(840478,7785030')<raw.index('terminate_once(840449,7784890'))
        self.assertTrue("NameHasOwner(':1.616878')"in raw)
        self.assertTrue('PG1368-bootstrap-fixed-ref-handoff-v1'in raw)
        self.assertTrue('pg1368-bootstrap-fixed-ref-handoff-v1'in raw)
        for old in ('Pg1356BootstrapExisting','/proc/839626','terminate_once(839655','PG1361_RECOVERY'):
            self.assertFalse(old in raw,old)
        self.assertTrue('free_snapshot()==proven'in raw)
        self.assertTrue('oldNormalClose'in raw)

if __name__=='__main__':
    unittest.main()
