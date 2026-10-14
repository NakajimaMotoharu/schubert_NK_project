"""Explicit new counts and actual context-free whole server syntax."""
import unittest
import pg2920_db_failure_group_full_qualified as p


class QualifierScope(unittest.TestCase):
    def test_exact_whole_counts_preserve_all_member_qualification(self):
        raw=p.server()
        for value in ['PG2918','3684',"'batch':(1284,173,568)",'morning_prefix',"'$Rows.class'",'DEBUG_SOURCE']:
            self.assertTrue(value in raw,value)
        self.assertNotIn('PG2798',raw)


if __name__=='__main__':unittest.main()
