"""Independent newcurrent verifier and allowed-delta whole post bindings."""
import unittest
from pyflakes.api import check
import pg1696_completed_publication_independent_post as p
import pg1691_completed_ordinary_publication_sources as factory


class PublicationPostTest(unittest.TestCase):
    def test_full_newsource_and_old_original_not_new_parent(self):
        raw=p.payload()
        self.assertEqual(0,check(raw,'<new published current independent post>'))
        for literal in ["data['source']['commit']=='2741c4546afad6c1e8b6efbd53dfb58144edf7bb'", "str(base/'pg1638-manifest.sig')",'len(rows)==24',"lines[-2:]==[b'0',b'0']", "if k!='startup'", "oracle['canonical_epoch'](expected_epoch)","oracle['verify'](public_first,public_last,'release'",'oldReceiptBug1154PreservedNotInferred', 'newSourceParentNotStarted', 'oldNativeNotAppliedToNewSource']:
            self.assertIn(literal,raw)
        for x in ['pidfd_send_signal','pg_terminate_backend','Files.move','os.rename']:self.assertNotIn(x,raw)

    def test_new_receipt_never_claims_zero_epoch_writes(self):
        raw=factory.sources()['Pg1691OrdinaryPublication.java']
        self.assertNotIn('startsStopsReloadsEpochWrites0=true',raw)
        self.assertIn('startsStopsReloadsSqlWrites0=true',raw)
        self.assertIn('canonicalEpochApprovalCurrentChanged=true',raw)
        # The old guest complete byte is preserved and validated only alongside
        # actual phase/current/epoch/old inode evidence, never patched in place.
        old=p.payload()
        self.assertIn('startsStopsReloadsEpochWrites0=true',old)
        self.assertIn("oracle['NEW_APPROVAL']",old)
        self.assertIn("oracle['OLD_LINK']",old)


if __name__=='__main__':unittest.main()
