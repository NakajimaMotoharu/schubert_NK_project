"""Actual generated guard, parent/child order, durable slots and full post scope."""
import ast
import unittest
import pg1382_role_fixed_ref_handoff as p

class Test(unittest.TestCase):
    def test_exact_current_pair_and_no_old_owner(self):
        seals = dict.fromkeys(p.previous.proof.previous.previous.previous.prior.prior.previous.transport.previous.SEALS, 'b'*64)
        raw = p.payload(seals)
        functions = {n.name: ast.get_source_segment(raw,n) for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)}
        self.assertIn('Pg1374BootstrapRolePreparation', functions['candidate'])
        self.assertIn('prepare', functions['candidate'])
        self.assertIn("'child':None", functions['parent_only'])
        self.assertIn("'bus':names", functions['fixed_owner'])
        self.assertLess(raw.index('terminate_once(841763,8003222'), raw.index('terminate_once(841734,8003102'))
        self.assertIn("NameHasOwner(':1.616973')",raw)
        self.assertIn('durable_reservation',raw)
        self.assertIn('free_snapshot()==proven',raw)
        self.assertIn('oldNormalClose',raw)
        self.assertIn('pg1382-role-fixed-ref-handoff-v1',raw)
        self.assertIn('PG1382-role-fixed-ref-handoff-v1',raw)
        for old in ('Pg1362BootstrapExisting','840449','840478','PG1368_RECOVERY','pg1367-bootstrap-failed-ref-pair-v1'):
            self.assertNotIn(old,raw)
        transport=p.source()
        self.assertIn('pg1382-role-fixed-ref-handoff-v1',transport)
        self.assertNotIn('pg1381-role-failed-ref-pair-v1',transport)

if __name__=='__main__':unittest.main()
