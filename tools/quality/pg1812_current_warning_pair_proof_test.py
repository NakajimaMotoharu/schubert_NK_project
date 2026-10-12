"""Actual emitted contract, UUID and full socket gates, no signal in proof."""
import ast
import unittest
from pg1812_current_warning_pair_proof import payload
import pg1812_warning_pool_contract_test as pool_fixture


class Actual(unittest.TestCase):
    def test_full_emitted_role_contract(self):
        raw=payload();tree=ast.parse(raw)
        node=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='validate_current_peers');ns={};exec(compile(ast.Module(body=[node],type_ignores=[]),'<actual emitted pool contract>','exec'),ns)
        self.assertEqual(479217,ns['validate_current_peers'](pool_fixture.Pools().fixture(2,2),1,479217)['pid'])
        self.assertFalse('signal.SIGTERM'in raw);self.assertTrue('4148e3e8-f107-431a-ab27-d6e6d1f1772e'in raw)
        self.assertTrue('len(left) == len(right) == 1'in raw)
        self.assertTrue('allCurrentPeersSocketBound'in raw)


if __name__=='__main__':unittest.main()
