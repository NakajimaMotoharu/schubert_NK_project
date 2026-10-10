"""Independent source/Root/fullscope/database/ADMIN contracts; no guest effects."""
import unittest
import pg983_current_bootstrap_sources as p
class Test(unittest.TestCase):
    def test_current_literal_tuple_release_and_original_completed_receipt(self):
        files=p.files('b'*64);joined='\n'.join(files.values())
        for x in ('40ef6e894573d2ffab1d1732124960f9c98d5f97','b75e8bd539edf40d1324896a16e51842d00a3983ba1eae661c86ab68d4692524','eeae04ea-713c-4f2d-888d-358fb4bed274','091663ce-1cf4-47e7-8311-218ebb0c8653','pg978-bootstrap-before-v2','202927375873','213904','201380374989'):
            self.assertTrue(x in joined,'missing '+x)
        for old in ('e01612fcd7f2752df5ae0836b78538fd5e87f120','PG862','pg895','pg887','Pg894'):self.assertFalse(old in joined,'old '+old)
    def test_whole_qualified_v3_scope_and_existingADMIN_preserved(self):
        files=p.files('b'*64);j=files['Pg983BootstrapExisting.java'];h=files['pg983_bootstrap_existing.py']
        for x in ('lease.confirmClosed()','maxGap','lease.verify()','Pg797OwnedDatabase'):
            self.assertTrue(x in j,'missing '+x)
        for x in ('global MODE,SAVE', 'all(config_same', '==594', "len(baseline['rows'])==24"):
            self.assertTrue(x in h,'missing '+x)
        self.assertTrue('complete_configuration' in h)
if __name__=='__main__':unittest.main()
