import unittest
import pg6638_current115_receivers as p


class SqlReceiverDefinitionTest(unittest.TestCase):
    def test_all57_raw_routes_are_explicit_disjoint(self):
        ids=[i for values in p.RAW_ROLES.values() for i in values]
        self.assertEqual(57,len(ids));self.assertEqual(57,len(set(ids)))
        self.assertEqual(set(p.RAW_ROLES),set(p.RAW_REASONS))
        for n in ids:self.assertIn(p.raw_role('SQLCATCH-'+str(n).zfill(3)),p.RAW_ROLES)
        with self.assertRaises(ValueError):p.raw_role('SQLCATCH-001')

    def test_caught_variable_and_first_statement_are_required(self):
        row=dict(siteId='SQLCATCH-001',category='GUARDED_REVIEW',catchVariable='x',beginLine=1)
        good='try {} catch(SQLException x) { Temp.preserveFatal(x); throw x; }'
        self.assertEqual('DIRECT_GUARD_BEFORE_MAPPING',p.review(row,good)['role'])
        for bad in (good.replace('preserveFatal(x)','preserveFatal(y)'),good.replace('Temp.','if(true) Temp.')):
            with self.assertRaises(ValueError):p.review(row,bad)

    def test_delayed_guard_requires_explicit_owned_scope(self):
        row=dict(siteId='SQLCATCH-106',category='GUARDED_REVIEW',catchVariable='x',beginLine=1)
        good='try {} catch(SQLException x) { try { c.rollback(); } finally {} Temp.preserveFatal(x); throw x; }'
        self.assertEqual('OWNED_CLEANUP_BEFORE_FINAL_GUARD',p.review(row,good)['role'])
        with self.assertRaises(ValueError):p.review(row,good.replace('try { c.rollback(); } finally {} ',''))


if __name__=='__main__':unittest.main()
