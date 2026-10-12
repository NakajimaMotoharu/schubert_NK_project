"""Actual newcurrent source, signed CLI, capacity and no old run replay."""
import unittest
from pyflakes.api import check
import pg1697_new_current_ordinary_before as p


class OrdinaryBeforeTest(unittest.TestCase):
    def test_noargs_before_is_readonly_not_authority(self):
        raw=p.payload()
        self.assertEqual(0,check(raw,'<ordinary newsource before>'))
        for literal in ['PG1638','2741c4546afad6c1e8b6efbd53dfb58144edf7bb',"'--resume'not in declaration[1]",'maintenance/active', '10737418240', "'originalBudgetSeconds':1800", "'oldCompletedRunNotResumed':True", "'authority':False"]:self.assertIn(literal,raw)
        for capability in ["systemctl','start",'pidfd_send_signal','pg_terminate_backend']:self.assertNotIn(capability,raw)


if __name__=='__main__':unittest.main()
