"""Full immutable role/stage/once activate/seven phase post graph guards, no action."""
import unittest
from pyflakes.api import check
import pg2856_network_cold_publication_stage as stage
import pg2858_network_cold_publication_activate as activate
import pg2860_network_cold_publication_post as post


class ColdPublicationGraph(unittest.TestCase):
    def test_all_roles_and_independent_seven_phase_post(self):
        a=stage.source();b=activate.source();c=post.payload()
        self.assertTrue('pg2854-network-cold-publication-frozen-v1.safe.json'in a)
        self.assertTrue("'Pg2852NetworkColdPublication','activate'"in b)
        for v in ['pg2852-network-cold-publication-tools-v1','79a3260a-e16d-42bf-942a-b914ed144c28']:
            self.assertTrue(v in a+b,v)
        self.assertTrue('pg2856-network-cold-publication-stage-v1'in b)
        self.assertTrue('pg2858-network-cold-publication-completed-v1'in b+c)
        for v in ['finiteColdActivation=true','link-staged.private.json','release.private.json','pub.verify_retained(',
            "'coldPublicationSevenPhasesVerified':True", "'newCanonicalInvalidNoPermission':True"]:
            self.assertTrue(v in c,v)
        self.assertEqual(0,check(c,'<whole seven-phase post>'))
        self.assertFalse('candidateNotActivated\':True'in c)


if __name__=='__main__':unittest.main()
