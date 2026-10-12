import ast
import unittest
from pg1546_pending_candidate_ro_sources import java,refs

class SourceTest(unittest.TestCase):
    def test_old_current_partial_and_new_candidate_are_not_confused(self):
        j=java();r=refs();ast.parse(r)
        self.assertIn('proof.completed().isEmpty()',j)
        self.assertIn('Pg387TrustedDeployment.LABEL="PG1544"',j)
        self.assertIn('Pg387TrustedDeployment.LABEL="PG1292"',j)
        self.assertIn('if(mountStatus==1)Pg387TrustedDeployment.freezeCandidate()',j)
        self.assertIn('mountStatus==0&&readonlyOptions',j)
        self.assertIn('if action in {\'prepared\',\'run\',\'release\'}:',r)
        self.assertIn('len(flags)==len(set(flags))',r)
        self.assertIn('contract.HeldInventory(str(candidate),candidate_rows,0).open()',r)
        self.assertIn('before_inventory=[h.capture()for h in held]',r)
        for banned in ['.activate(','.invalidate(','.revoke(','StartUnit','StopUnit','daemon-reload']:
            self.assertNotIn(banned,j+r)

if __name__=='__main__':unittest.main()
