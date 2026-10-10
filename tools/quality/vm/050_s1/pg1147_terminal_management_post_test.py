import ast
import hashlib
import unittest
from pg1147_terminal_management_post import payload,INVALID


class PostTest(unittest.TestCase):
    def test_independent_invalid_vector_full_originals_and_no_operations(self):
        text=payload();ast.parse(text)
        self.assertEqual(len(INVALID),264)
        self.assertEqual(hashlib.sha256(INVALID).hexdigest(),'b54c6d46594575e9c46f3d2e46e8a282f657bfeca6f194a38060f3533684e72d')
        for part in ['terminal-management-post-v1',"ActiveState='inactive',SubState='dead'",'expected_startup',
                     'oldPermitOwnerPreserved','allPeersAdvisoryMaintenanceAdmission0','operationAuthority',
                     'observed=post();require(observed==post())','require(observed==post())','manager.UnrefUnit(u)','bus.close()']:
            self.assertTrue(part in text,part)
        for part in ['systemctl stop','systemctl start','pidfd_send_signal','os.kill(']:
            self.assertFalse(part in text,part)


if __name__=='__main__':unittest.main()
