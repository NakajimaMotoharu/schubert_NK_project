"""No old normal-close inflation; full baseline/finite delta/fresh resources remain."""
import unittest
import pg1391_prepared_role_independent_baseline as p

class Test(unittest.TestCase):
    def test_sent_baseline_closed_scope(self):
        raw=p.payload(dict.fromkeys(p.previous.previous.previous.previous.transport.previous.SEALS,'b'*64))
        for s in ('pg1391-prepared-role-independent-baseline-v1',"result['preparationNormalClose']=False",'role_policy.delta',"'parentPid1':receipt_rows",'allClientAdvisoryFlock0','recovered[\'native\']==native','pg1344-current-bootstrap-before-v1/after.private.json'):
            self.assertIn(s,raw)
        self.assertNotIn("prepared==closed",raw)
        self.assertNotIn("prepared_root/'complete.private'",raw)
        self.assertNotIn("result['preparationNormalClose']=True",raw)
        compile(raw,'<actual failed-role baseline>','exec')

if __name__=='__main__':unittest.main()
