"""New-only transport/place/post complete graph guards, no guest operation."""
import unittest
from pyflakes.api import check
import pg2836_network_cold_unused_stage as stage
import pg2838_network_cold_unused_place as place
import pg2840_network_cold_unused_post as post


class ColdUnusedGraph(unittest.TestCase):
    def test_all_exact_roles_and_action(self):
        a=stage.source();b=place.source();c=post.payload()
        self.assertEqual('pg2834-network-cold-unused-frozen-v1.safe.json',place.FROZEN)
        self.assertTrue(place.FROZEN in a)
        for value in ['pg2832-network-cold-unused-tools-v1','79a3260a-e16d-42bf-942a-b914ed144c28']:
            self.assertTrue(value in a,value);self.assertTrue(value in b,value)
        self.assertTrue("'Pg2832NetworkColdUnusedCandidate','place'"in b)
        self.assertTrue('pg2836-network-cold-unused-stage-v1'in b)
        self.assertTrue('pg2838-network-cold-unused-completed-v1'in b+c)
        self.assertTrue('unusedCandidatePlacement=true'in c)
        self.assertTrue('37bfe01a075449d36cc8b73408dd81fc6d6efc158910a437cbde21b6a0b7f863'in c)
        self.assertEqual(0,check(c,'<whole real unused post>'))
        for v in ['pg1079-cold-candidate-v1','PG1068','env[','11678','11704']:
            self.assertFalse(v in c,v)
        self.assertTrue("first==snapshot()and runtime==runtime_check()"in c)
        self.assertTrue('parentBackendAdvisoryFlocksGone'in c)


if __name__=='__main__':unittest.main()
