"""Pure completed role graph tests; no dispatch or tool PT counted as Production."""
import unittest
from pyflakes.api import check
import pg2820_network_current_cold_stage as stage
import pg2822_network_current_cold_prepare as prepare
import pg2830_network_current_cold_post as post
from pg2816_network_current_cold_sources import CLASS,SOURCE,BOOT,TOOLS,DONE_SHA


class CompleteNewBootRoles(unittest.TestCase):
    def test_stage_and_dispatch_complete_immutable_tuple(self):
        s=stage.source();r=prepare.source()
        for value in [BOOT,SOURCE,TOOLS,'pg2818-network-current-cold-frozen-v1.safe.json']:self.assertTrue(value in s,value)
        for value in [BOOT,CLASS,TOOLS,'pg2820-network-current-cold-stage-v1','0.1.0-PG2654','pg2822-network-current-cold-prepared-v1']:self.assertTrue(value in r,value)
        self.assertNotIn('/proc/3323',r)
        self.assertNotIn('PG2126',s+r)

    def test_post_strict_resource_and_original_closure(self):
        r=post.payload();self.assertEqual(0,check(r,'<whole post>'))
        for value in [BOOT,SOURCE,DONE_SHA,'pg2830-network-current-cold-independent-post-v1',
            'pg2822-network-current-cold-prepared-v1',"first==before['current'] and first==snapshot()",
            'contract.free_flocks(',"'parentBackendAdvisoryFlocksGone':True","'permissionIssued':False",
            '26250063-8755-43b6-9ac7-f76d5eee7257','0.1.0-PG2654']:
            self.assertTrue(value in r,value)
        self.assertNotIn('PG1292',r);self.assertNotIn('PG2126',r)


if __name__=='__main__':unittest.main()
