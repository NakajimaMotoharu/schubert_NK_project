import ast
import unittest
from pg2309_current_resume_pair_proof import payload,PID,CHILD,BACKEND


class PairProof(unittest.TestCase):
    def test_full_readonly_exact_current_pair_scope(self):
        raw=payload()
        for value in ['e7456ef531cde4d5e09161f401861ad0f718febbe786e59038e46dc869298a1e','0.1.0-PG2126','09640d25fa96fd2599a0a3e3e52bbb20331501bf245c51a762dab611d3a8ac5a',str(PID),str(CHILD),str(BACKEND),'runtimeDirectoryAbsent','same_peer','fd_relation']:
            self.assertIn(value,raw)
        for value in ['SIGTERM','pidfd_send_signal','daemon-reload','498727','498758','498756']:
            self.assertNotIn(value,raw)
        self.assertIn('len(rows) == 24',raw)
        self.assertIn('len(a[\'fds\']) == 101',raw)
        self.assertIn('same_peer()',raw)
        ast.parse(raw)


if __name__=='__main__':unittest.main()
