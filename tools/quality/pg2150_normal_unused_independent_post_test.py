import unittest
import pg2150_normal_unused_independent_post as p


class Post(unittest.TestCase):
    def test_actual_normal_and_two_source_roles(self):
        raw=p.payload()
        for value in ['pg2148-current-normal-unused-placement-v1','genuineParentNormalWarningOriginal=true','currentManagerGc=true','0.1.0-PG2126','3b7f3567b54f91f3a9dbeb859e8dd77e8353a2c8','62213f357c9dab3b00b557549426b091a03ace6557a62f4410999a02028a332c','7ef03cf927c2f5b79b39a5d5187db439c753c57933bfff18b26386a02afaf449','/opt/schubert-nk/releases/0.1.0-PG1846','75669b01c69e4ecc2459e73dbd3e0a6abcac7cdfaf6ce4095561314d533b1eb4']:
            self.assertIn(value,raw)
        self.assertIn("lines[-2:] == [b'0', b'0']",raw)
        self.assertNotIn('pidfd_send_signal',raw)
        self.assertNotIn('managerFailureRetained=true',raw)
        self.assertNotIn('pg1684-completed-unused-placement-v4',raw)


if __name__=='__main__':unittest.main()
