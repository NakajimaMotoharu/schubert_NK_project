import ast
import unittest
from pg1549_pending_candidate_ro_once import valid_receipt,source

class OnceTest(unittest.TestCase):
    def test_actual_mount_and_normal_frame(self):
        v=b'PG1292 STAGE PINNED_SIGNATURE_VERIFIED\nPG1292 STAGE FULL_CANDIDATE_BOM_VERIFIED\nPG1544 STAGE FIXED_CANDIDATE_HOST_RO\nPG1544 STAGE PINNED_SIGNATURE_VERIFIED\nPG1544 STAGE FULL_CANDIDATE_BOM_VERIFIED\nPG1549_DONE candidateHostRo=true allScopesReturnedNormally=true originalRetiredOrAuthorityIssued=false\n'
        self.assertTrue(valid_receipt(v))
        for bad in [None,v.decode(),v[:-1],v+b'extra\n',v.replace(b'PG1544 STAGE FIXED_CANDIDATE_HOST_RO\n',b''),v.replace(b'allScopesReturnedNormally=true',b'allScopesReturnedNormally=false')]:self.assertFalse(valid_receipt(bad))

    def test_frozen_mode_and_no_replay(self):
        t=ast.parse(source());args=next(n.value for n in ast.walk(t)if isinstance(n,ast.Assign)and any(isinstance(x,ast.Name)and x.id=='args'for x in n.targets))
        self.assertEqual(ast.literal_eval(args.right)[-2:],['Pg1546PendingCandidateHostRo','prepare-ro'])
        self.assertIn('out.mkdir(mode=0o700)',source())
        self.assertIn('success=result.returncode==0 and valid_receipt(log)',source())

if __name__=='__main__':unittest.main()
