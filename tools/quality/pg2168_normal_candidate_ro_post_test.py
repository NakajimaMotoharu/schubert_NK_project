import unittest
import pg2168_normal_candidate_ro_post as p


class Post(unittest.TestCase):
    def test_actual_normal_mount_and_two_role_post(self):
        raw=p.payload()
        for text in ['pg2167-normal-candidate-host-ro-v1','candidateReadOnlyVerified=true','genuineParentNormalWarningOriginal=true','currentManagerGc=true','--mountpoint','/opt/schubert-nk/releases/0.1.0-PG2126','/opt/schubert-nk/releases/0.1.0-PG1846']:self.assertIn(text,raw)
        self.assertNotIn('unusedCandidatePlaced=true',raw)
        self.assertNotIn('0.1.0-PG1638',raw)
        self.assertNotIn('pidfd_send_signal',raw)
        self.assertIn("'ro'in mounts and 'rw'not in mounts",raw)


if __name__=='__main__':unittest.main()
