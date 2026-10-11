"""Current actual parent/child ownership, irreversible ordering and no prepare replay."""
import unittest
import pg1390_prepared_role_fixed_pair_handoff as p

class Test(unittest.TestCase):
    def test_current_generated_pair(self):
        raw=p.payload(dict.fromkeys(p.previous.previous.proof.previous.previous.previous.prior.prior.previous.transport.previous.SEALS,'b'*64))
        self.assertLess(raw.index('terminate_once(842946,8059148'),raw.index('terminate_once(842917,8059022'))
        for s in ('Pg1380BootstrapRolePreparation','pg1390-prepared-role-fixed-pair-v1','PG1390-prepared-role-fixed-pair-v1',"NameHasOwner(':1.617058')",'free_snapshot()==proven',"'prepared.private.json'",'durable_reservation'):
            self.assertIn(s,raw)
        for s in ('Pg1374BootstrapRolePreparation','841734','841763','PG1382_RECOVERY','mkdirat','Pg1370BootstrapRoleDirectory.prepare'):
            self.assertNotIn(s,raw)
        compile(raw,'<actual prepared pair>','exec')

if __name__=='__main__':unittest.main()
