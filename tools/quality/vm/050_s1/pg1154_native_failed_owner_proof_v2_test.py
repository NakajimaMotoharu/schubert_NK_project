import ast
import unittest
from pg1154_native_failed_owner_proof_v2 import payload


class ProofTest(unittest.TestCase):
    def test_fixed_actual_zero_not_old_normal_close(self):
        s=payload();tree=ast.parse(s)
        f=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='resource_zero'][-1];fragment=ast.unparse(f)
        self.assertFalse('live'in fragment);self.assertTrue("[b'0', b'0']"in fragment)
        self.assertTrue("'oldNormalClose':False"in s)
        self.assertTrue('native-failed-owner-proof-v2'in s)


if __name__=='__main__':unittest.main()
