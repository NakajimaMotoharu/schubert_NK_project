"""Whole RO compiler/stage/action/post role contracts, actual operation disabled."""
import unittest
from pyflakes.api import check
import pg2846_network_cold_ro_stage as stage
import pg2848_network_cold_ro_prepare as prepare
import pg2850_network_cold_ro_post as post


class ColdRoGraph(unittest.TestCase):
    def test_exact_whole_family(self):
        a=stage.source();b=prepare.source();c=post.payload()
        self.assertTrue('pg2844-network-cold-ro-frozen-v1.safe.json'in a)
        self.assertTrue("'Pg2842NetworkColdCandidateRo','prepare-ro'"in b)
        for value in ['pg2842-network-cold-ro-tools-v1','79a3260a-e16d-42bf-942a-b914ed144c28']:
            self.assertTrue(value in a+b,value)
        self.assertTrue('pg2846-network-cold-ro-stage-v1'in b)
        self.assertTrue('pg2848-network-cold-ro-completed-v1'in b+c)
        self.assertTrue('candidateImmutableVerified=true'in c)
        self.assertTrue("'ro'in ro_flags and 'rw'not in ro_flags"in c)
        self.assertEqual(0,check(c,'<full current RO post>'))
        self.assertFalse('unusedCandidatePlacement=true'in c)


if __name__=='__main__':unittest.main()
