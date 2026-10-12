"""Independent current pair bindings and no mutation capability checks."""
import unittest
from pyflakes.api import check
import pg1664_current_unused_pair_readonly_proof as p


class CurrentPairProofTest(unittest.TestCase):
    def test_exact_current_identity_and_peer(self):
        raw = p.payload()
        for literal in ['5962776', '5962938', '291211', '291242', '291240', 'pg1659-completed-unused-tools-v3', "children=={291242}", "set(fds)=={'0','1','2','3'}", "len(a['fds'])==101", "peer['state']=='idle in transaction'", "objid=71419602"]:
            self.assertIn(literal, raw)
        for old in ['289328', '5627480', 'pg1650-retained-no-db-proof-v1', "'noChild':True", "'clientAdvisory0':True"]:
            self.assertNotIn(old, raw)

    def test_full_source_and_readonly_capabilities(self):
        raw = p.payload()
        self.assertEqual(0, check(raw, '<current pair full proof>'))
        for capability in ['pidfd_send_signal', 'os.kill(', 'pg_terminate_backend', "systemctl','start", 'tar.extractall']:
            self.assertNotIn(capability, raw)
        for oracle in ['len(rows)==24', 'len(data[\'artifacts\'])==187', "lines[-2:]==([b'0',b'0']if PEER_CLOSED else[b'1',b'1'])", 'libc.syscall(312,291213,291213,0,a,b)', 'before.private.json', 'nativeCurrent']:
            if oracle == 'nativeCurrent':
                self.assertIn('independent_native_catalog()', raw)
            else:
                self.assertIn(oracle, raw)

    def test_four_case_fd_oracle(self):
        self.assertEqual(3, len(p.prior.fd_relation('maintenance.lock', ['30', '33', '34'], ['34'], lambda a, b: 1)))
        self.assertEqual([{'a': '43', 'b': '128', 'sameOfd': True}], p.prior.fd_relation('startup-admission.lock', ['43', '128'], ['43', '128'], lambda a, b: 0))
        for result in [0, -1, True, None]:
            with self.assertRaises(ValueError):
                p.prior.fd_relation('maintenance.lock', ['30', '33', '34'], ['34'], lambda a, b: result)


if __name__ == '__main__':
    unittest.main()
