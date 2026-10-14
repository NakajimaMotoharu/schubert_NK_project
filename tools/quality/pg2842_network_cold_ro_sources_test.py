"""Literal finite-RO guards, graph and no cold/placement replay."""
import unittest
from pyflakes.api import check
import pg2842_network_cold_ro_sources as p


class ColdRo(unittest.TestCase):
    def test_exact_newboot_current_and_candidate_tuple(self):
        j=p.java();r=p.observer()
        self.assertEqual(0,check(r,'<full RO graph>'))
        for v in [p.CLASS,'79a3260a-e16d-42bf-942a-b914ed144c28','04207efc3ad78bca75942153a90c70985064c988',
            'a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25','0.1.0-PG2654','0.1.0-PG2802']:
            self.assertTrue(v in j,v)
        self.assertTrue('"prepare-ro".equals(args[0])'in j)
        self.assertTrue('Files.readSymbolicLink(Path.of("/proc/1/ns/mnt"))'in j)
        self.assertTrue('FULL_IMMUTABLE_CANDIDATE'in j)
        self.assertTrue("authenticate();authenticate_candidate();fixed_parent=actor();before_inventory="in r)
        self.assertTrue("'ro'in opts and 'rw'not in opts"in r)
        for v in ['place_candidate()', 'tar.extractall(', 'BUNDLE_HASH','FINITE_EMPTY_NAMESPACES','issuePermit','invalidate(']:
            self.assertFalse(v in j+r,v)
        self.assertTrue('locks.owned_flocks('in r)
        self.assertTrue('PEER_CLOSED=True'in r)


if __name__=='__main__':unittest.main()
