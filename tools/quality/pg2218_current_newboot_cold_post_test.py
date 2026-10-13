import unittest
from pg2218_current_newboot_cold_post import payload


class IndependentPost(unittest.TestCase):
    def test_all_literals_and_normal_resource_closure_not_just_metadata(self):
        s=payload()
        for v in ['pg2218-current-newboot-cold-independent-post-v1','PG2218-current-newboot-cold-independent-post-v1',
          'pg2212-current-newboot-cold-prepared-v1','25282e2790274c2564332c128125d3f18c77b78982aad4f96eb84c463ab3c91c',
          '20b86040-ffd5-4d17-9fca-5d83048ba905','0.1.0-PG2126',
          "first==before['current'] and first==snapshot()",'contract.free_flocks(',
          "'parentBackendAdvisoryFlocksGone':True", "'permissionIssued':False"]:
            self.assertIn(v,s)
        self.assertNotIn('59f3b401',s)
        self.assertNotIn('0.1.0-PG1292',s)
        self.assertNotIn('systemctl start',s)


if __name__=='__main__':unittest.main()
