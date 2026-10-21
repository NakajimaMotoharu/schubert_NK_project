import unittest
from pg6624_jdbc_current_inventory import align,FACTORY


class StableSqlSiteTest(unittest.TestCase):
    def test_original049_retained_and_new_two_are_explicit(self):
        rows=align(FACTORY,[{'siteId':'SQLCATCH-049'}],[{'catchVariable':n} for n in ('failure','secondary','failure')])
        self.assertEqual(['SQLCATCH-114','SQLCATCH-115','SQLCATCH-049'],[r[0] for r in rows])
        self.assertIsNone(rows[0][1]);self.assertEqual('SQLCATCH-049',rows[2][1]['siteId'])
        with self.assertRaises(ValueError):align(FACTORY,[{'siteId':'SQLCATCH-048'}],[{'catchVariable':'failure'}]*3)
        with self.assertRaises(ValueError):align(FACTORY,[{'siteId':'SQLCATCH-049'}],[{'catchVariable':'failure'}]*2)

    def test_other_identity_cannot_shift_or_hide_new_scope(self):
        self.assertEqual('SQLCATCH-010',align('other',[{'siteId':'SQLCATCH-010'}],[{'catchVariable':'x'}])[0][0])
        with self.assertRaises(ValueError):align('other',[{'siteId':'SQLCATCH-010'}],[])


if __name__=='__main__':unittest.main()
