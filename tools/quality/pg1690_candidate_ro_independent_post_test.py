"""Independent ordinary current preservation and exact host mount-only post."""
import unittest
from pyflakes.api import check
import pg1690_candidate_ro_independent_post as p


class CandidateRoPostTest(unittest.TestCase):
    def test_full_current_187_and_host_namespace_mount(self):
        raw=p.payload()
        self.assertEqual(0,check(raw,'<candidateRO independent full post>'))
        for text in ['len(rows)==24',"lines[-2:]==[b'0',b'0']","len(c['artifacts'])==187",'candidateReadOnlyVerified=true','candidateHostReadonlyVerified',"'/proc/self/ns/mnt'", "'ro'in mounts and 'rw'not in mounts",'pg1689-completed-candidate-host-ro-v1']:
            self.assertIn(text,raw)
        for text in ['tar.extractall','pidfd_send_signal','pg_terminate_backend','candidate=Pg387']:self.assertNotIn(text,raw)


if __name__=='__main__':unittest.main()
