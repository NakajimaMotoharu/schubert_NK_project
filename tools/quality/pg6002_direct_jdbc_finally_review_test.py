import unittest
from pg6002_direct_jdbc_finally_review import require_finally,require_helper,block_helper


class DirectCloseContractReviewTest(unittest.TestCase):
    def test_only_once_close_with_exact_guard_and_no_normal_return(self):
        good='finally { try { row.close(); } catch (SQLException | RuntimeException | Error secondary) { if (replace(rowFailure, secondary)) throw secondary; } }'
        self.assertEqual((['row'],[('rowFailure','secondary')]),require_finally(good,'replace'))
        for bad in (good.replace('if (replace(rowFailure, secondary)) ',''),good.replace('row.close();','row.close(); row.close();'),good.replace('throw secondary;','return;'),good.replace('replace(rowFailure','foreign(rowFailure')):
            with self.assertRaises(ValueError):require_finally(bad,'replace')

    def test_unknown_identity_and_fixed_secondary_helpers_required(self):
        good='if(primary == null || (primary instanceof SQLException && !(secondary instanceof SQLException))) return true; if (!(primary instanceof SQLException)) primary.addSuppressed(new Fixed()); return false;'
        require_helper(good,'SQL')
        for bad in (good.replace('primary == null','primary != null'),good.replace('primary.addSuppressed(','secondary.addSuppressed('),good.replace('return false;','return true;')):
            with self.assertRaises(ValueError):require_helper(bad,'SQL')

    def test_session_connection_and_inner_borrowed_resources_have_distinct_fixed_helpers(self):
        for owner in ('batch/repository/CleanupDatabaseSession','batch/repository/MorningDatabaseSession'):
            self.assertEqual('closeReplace',block_helper(owner,'owned.close(); connection.close();','closeReplace'))
            for resource in ('rows','statement'):
                self.assertEqual('JdbcResourceFailures.replace',block_helper(owner,resource+'.close();','closeReplace'))
            with self.assertRaises(ValueError):block_helper(owner,'foreign.close();','closeReplace')
        body='finally { try { connection.close(); } catch (SQLException | RuntimeException | Error secondary) { if (replace(connectionFailure, secondary)) throw secondary; } }'
        self.assertEqual((['connection'],[('connectionFailure','secondary')]),require_finally(body,'replace'))


if __name__=='__main__':
    unittest.main()
