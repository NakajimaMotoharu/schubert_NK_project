"""Whole actual current role+ADMIN closure without aliasing before/after or GC success."""
import ast
import unittest
import pg1400_existing_admin_independent_post as p

class Test(unittest.TestCase):
    def test_whole_sent_contract(self):
        raw=p.payload(dict.fromkeys(p.previous.previous.previous.previous.previous.previous.transport.previous.SEALS,'b'*64))
        for fragment in ('pg1395-existing-role-normal-post-v1/after.private.json','pg1400-existing-admin-independent-post-v1','current_normal_or_gc','native==boot_after','all24UnchangedTwice','whole187SignedArtifactBytesVerified','currentCredentialsRetired',"initial['current']==prepared['current']==old_after", "verified_initial['native']==verified_prepared['native']==boot_before['native']",'ordinary-bootstrap196','ADMIN_HASHES'):
            self.assertIn(fragment,raw)
        self.assertLess(raw.index('manager.RefUnit(u)'),raw.index('current_bootstrap=show'))
        self.assertLess(raw.index('current_bootstrap=show'),raw.index(' def snapshot():'))
        self.assertNotIn('pg1400-existing-admin-independent-post-v1/after.private.json',raw)
        ast.parse(raw)

if __name__=='__main__':unittest.main()
