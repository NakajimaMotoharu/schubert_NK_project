"""Current ABI/pre-ownership source closure, independent exact tuple oracle."""
import unittest
from pg1728_bootstrap_abi_sources import files

class AbiSourcesTest(unittest.TestCase):
    def test_current_abi_boundary_before_locks(self):
        result=files('6b29aa3fbeee305335bba17f2fe40f51041a3197cc17c9795a9ddd949930c838')
        java=result['Pg1728BootstrapExisting.java']
        pre='beforeOwnership(()->{verifyInputClosure();expectedBeforeOwnership(2,"schubert_batch","PG1728-bootstrap-guard","schubert_nk",true,true);});'
        self.assertIn(pre,java);self.assertLess(java.index(pre),java.index('require(MaintenanceFileLock.create().tryExclusive('))
        self.assertNotIn('Pg797OwnedDatabase',java)
        self.assertIn('PG[0-9]{3,4}-[a-z-]{1,32}',result['Pg1728OwnedDatabase.java'])
        self.assertIn('if(role==null||application==null||database==null)throw new IllegalArgumentException',result['Pg1728OwnedDatabase.java'])
        self.assertIn('pg1728-current-bootstrap-abi-tools-v1',result['pg1728_input_preflight.py'])
        self.assertIn('pg1703_parent_receipt.py',result)
        self.assertIn('lease.confirmClosed()',java)
        self.assertIn('Pg387TrustedDeployment.STEM="pg1638"',java)

if __name__=='__main__':unittest.main()
