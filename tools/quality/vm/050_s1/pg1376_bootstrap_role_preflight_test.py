"""Actual complete guard, independent literals and old actor stops forbidden."""
import ast
import unittest
import pg1376_bootstrap_role_preflight as p

class Test(unittest.TestCase):
    def test_actual_sent_guard_complete(self):
        raw=p.payload(dict.fromkeys(p.previous.previous.transport.previous.SEALS,'b'*64));ast.parse(raw)
        for value in ('policy.before_valid(native)','not os.path.lexists(role)',"b'999'", "b'981'", 'PG1376-bootstrap-role-preflight-v1','pg1376-bootstrap-role-preflight-v1',"lines[-2:]==[b'0',b'0']"):
            self.assertTrue(value in raw,value)
        for old in ('PG1340-published-terminal-post-v4','systemctl start','pidfd_send_signal'):
            self.assertFalse(old in raw,old)

if __name__=='__main__':unittest.main()
