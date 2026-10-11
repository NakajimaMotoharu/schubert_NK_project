"""Whole actual prepared phase proof binds immutable old baseline and new finite delta."""
import unittest
import pg1389_role_prepared_failed_pair_proof as p

class Test(unittest.TestCase):
    def test_whole_generated_scope(self):
        raw=p.payload(dict.fromkeys(p.previous.previous.previous.previous.previous.prior.prior.previous.transport.previous.SEALS,'b'*64))
        for s in ('Pg1380BootstrapRolePreparation','pg1380-bootstrap-role-tools-v2','pg1380-bootstrap-role-prepare-v1',"'prepared.private.json'",'role_policy.delta','prepared[\'native\']==native','pg1344-current-bootstrap-before-v1','pg1389-role-prepared-failed-pair-v1','owner==fixed_owner()','expiredDbPeerGone'):
            self.assertIn(s,raw)
        self.assertNotIn('Pg1374BootstrapRolePreparation',raw)
        self.assertNotIn('terminate_once(',raw)
        self.assertNotIn('signal.pidfd_send_signal(',raw)
        compile(raw,'<full actual phase proof>','exec')

if __name__=='__main__':unittest.main()
