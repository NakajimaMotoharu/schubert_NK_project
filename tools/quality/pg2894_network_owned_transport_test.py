"""Final STAGE/run namespace (embedded payload), newslots and retained qualified helpers."""
import unittest
from pyflakes.api import check
import pg2894_network_owned_dispatch as p


class OwnedTransport(unittest.TestCase):
    def test_final_stage_boot_source_archive_and_unique_retries(self):
        s=p.stage();r=p.run_source()
        self.assertEqual(0,check('DIGEST="a"\nFILES=set()\n'+s,'<actual final stage>'))
        for v in ['79a3260a-e16d-42bf-942a-b914ed144c28','a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25',
            '37bfe01a075449d36cc8b73408dd81fc6d6efc158910a437cbde21b6a0b7f863','pg2894-network-owned-stage-v2','pg2894-v2-pg2890-network-owned-stop-tools-v1.tar']:
            self.assertTrue(v in s,v)
        self.assertFalse('b2d6f605'in s)
        self.assertTrue("('pg2894-' + action + '-v2')"in r)
        self.assertTrue('pg2894-stage-v2.exit'in r)
        self.assertFalse('pg2894-stage-v1.exit'in r)
        self.assertTrue('pg2892-frozen-v1.safe.json'in r)


if __name__=='__main__':unittest.main()
