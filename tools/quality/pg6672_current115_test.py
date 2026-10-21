import unittest
import pg6672_current115_receivers as p


class RelocatedCatchIdentityTest(unittest.TestCase):
    def test_only_line_movement_is_rebound_and_old_record_retained(self):
        old='try { work(); } catch (SQLException fault) { preserveFatal(fault); throw fixed("literal"); }'
        rows=[dict(p.sites(old)[0],siteId='SQLCATCH-001',sourceSha256='old')]
        result=p.rebound(rows,old,'\n\n'+old,p.RELOCATED)
        self.assertEqual(1,result[0]['originalBeginLine']);self.assertEqual(3,result[0]['beginLine'])
        self.assertEqual('old',result[0]['originalSourceSha256']);self.assertEqual(1,rows[0]['beginLine'])
        with self.assertRaises(ValueError):p.rebound(rows,old,'\n'+old,'unreviewed.java')

    def test_literal_type_variable_body_and_missing_or_extra_scope_rejected(self):
        old='try { work(); } catch (SQLException fault) { preserveFatal(fault); throw fixed("literal"); }'
        rows=[dict(p.sites(old)[0],siteId='SQLCATCH-001',sourceSha256='old')]
        for new in (old.replace('literal','changed'),old.replace('fault','other'),old.replace('preserveFatal','discard'),old+old,''):
            with self.assertRaises(ValueError):p.rebound(rows,old,new,p.RELOCATED)
        self.assertEqual(p.sites(old)[0]['bodyTokenSha256'],p.sites(old.replace('literal','changed'))[0]['bodyTokenSha256'])
        self.assertNotEqual(p.exact_catches(old),p.exact_catches(old.replace('literal','changed')))


if __name__=='__main__':unittest.main()
