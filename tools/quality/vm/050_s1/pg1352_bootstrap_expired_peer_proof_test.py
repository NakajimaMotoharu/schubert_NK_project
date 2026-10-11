"""Actual zero-peer matrix distinguishes expiry from normal ownership return."""
import unittest
import pg1352_bootstrap_expired_peer_proof as p

class Test(unittest.TestCase):
    def test_current_expired_contract_not_peer_imputation(self):
        raw = p.payload(dict.fromkeys(p.previous.prior.prior.previous.transport.previous.SEALS, 'b' * 64))
        compile(raw, '<expired proof>', 'exec')
        self.assertNotIn('peer[', raw)
        self.assertNotIn("lines[-2:]==[b'1',b'1']", raw)
        self.assertIn("lines[-2:]==[b'0',b'0']", raw)
        self.assertIn("expiredDbPeerGone':True", raw)
        self.assertIn("oldNormalClose=False", raw)
        self.assertIn("['FLOCK','ADVISORY','WRITE',str(owner['pid'])]", raw)
        self.assertIn('owner==fixed_owner()', raw)
        self.assertNotIn('pidfd_send_signal', raw)

if __name__ == '__main__':
    unittest.main()
