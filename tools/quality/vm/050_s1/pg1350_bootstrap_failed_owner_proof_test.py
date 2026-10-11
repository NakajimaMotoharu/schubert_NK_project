"""Actual full proof composition, immutable baseline and same-peer boundaries."""
import ast
import unittest
import pg1350_bootstrap_failed_owner_proof as p

class Test(unittest.TestCase):
    def test_complete_fixed_owner_payload(self):
        raw = p.payload(dict.fromkeys(p.prior.previous.transport.previous.SEALS, 'b' * 64))
        ast.parse(raw)
        self.assertIn("lines[-2:]==[b'1',b'1']", raw)
        self.assertNotIn("lines[-2:]==[b'0',b'0']", raw)
        for expected in ('PG1348-bootstrap-guard', 'Pg1348BootstrapExisting',
                         'Pg1334', 'sameRunActivationCutoff',
                         "owner==fixed_owner()", "current':after"):
            if expected == 'sameRunActivationCutoff':
                self.assertIn("summary=e['completed']", raw)
            elif expected == 'Pg1334':
                self.assertIn('pg1334-native-tools-v1', raw)
            else:
                self.assertIn(expected, raw)
        self.assertNotIn('pidfd_send_signal', raw)
        self.assertNotIn('systemctl start', raw)
        self.assertIn('len(candidates)==1', raw)
        self.assertIn('r[9]in sockets', raw)
        self.assertIn("metadata9(st)", raw)

if __name__ == '__main__':
    unittest.main()
