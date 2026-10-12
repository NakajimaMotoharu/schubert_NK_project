import ast
import unittest
from pg1505_publication_recovery_sources_v3 import java,refs

class CurrentRecoveryV3Test(unittest.TestCase):
    def test_fixed_new_bindings_and_no_fd_fabrication(self):
        j=java();r=refs();compile(r,'<corrected current owner source>','exec')
        self.assertIn('Pg1505PublicationOnlyRecovery',j);self.assertIn('pg1507-publication-only-recovery-v3',j)
        self.assertIn('pg1505_publication_recovery_refs.py',j)
        self.assertIn('kernel_contract.validate(lines,41805,fd_keys,maps)',r)
        self.assertNotIn('require(matches)',r)
        self.assertIn('os.O_RDONLY|os.O_NOFOLLOW',r)
        self.assertIn('(994,979,0o600,1,32768)',r)
        self.assertIn('locks.owned_flocks',r) # M/A still requires actual FD-owned inode/FLOCK.
        self.assertIn('age<1800',r)
        self.assertIn('BROKER_LOCKS is not None',r)
        self.assertNotIn('.revoke(',j);self.assertNotIn('.invalidate(',j)
        self.assertTrue(any(isinstance(n,ast.FunctionDef)and n.name=='kernel_scope'for n in ast.parse(r).body))

if __name__=='__main__':unittest.main()
