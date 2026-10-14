"""Actual capacity gate exact boundary/null/type and source/once/old failure separation."""
import inspect
import unittest
import pg2872_network_newcurrent_once_v2 as p
import pg2860_network_cold_publication_post as post
import pg2866_network_capacity_before as before
import pg2870_network_capacity_post as after
from pyflakes.api import check


class OnceCapacity(unittest.TestCase):
    def test_strict_capacity_boundary_keeps_12gib(self):
        p.require_capacity(12884901888);p.require_capacity(12884901889)
        for v in [12560904192,12884901887,None,False,True,12884901888.0,'12884901888',-1]:
            with self.assertRaises(ValueError):p.require_capacity(v)

    def test_complete_v2_independent_before_and_no_wrong_source(self):
        raw=p.payload({'pg2862_watch_parent.py':'a'*64})
        self.assertEqual(0,check(raw,'<complete oncev2 graph>'))
        self.assertTrue(p.SLOT in raw)
        self.assertFalse(p.prior.SLOT in raw)
        self.assertTrue('require_capacity(os.statvfs('in raw)
        self.assertLess(raw.index("persist('external-start-guard.private.json'"),raw.index("['/usr/bin/systemctl','start','--no-block'"))
        self.assertTrue("'replayAllowed':False"in raw)
        self.assertTrue("'newBootRuntimeExecCount':0"in raw)
        self.assertTrue('originalBudgetSeconds=1800'in raw)
        for fn in [post.payload,before.payload,after.payload]:self.assertEqual(0,check(fn(),'<whole capacity crossscope actual graph>'))
        self.assertTrue('sameBootOnlineCapacity'in inspect.getsource(p.main))


if __name__=='__main__':unittest.main()
