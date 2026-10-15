"""Complete current source namespace; expected precedence is independent fixed data."""
import unittest
from pathlib import Path
from pyflakes.api import check
from pg3254_recheck_statement_selected import server, METHOD, TEST


class RecheckStatement(unittest.TestCase):
    def test_whole_namespace_and_no_main_or_guest_mutation(self):
        raw = server('statement')
        self.assertEqual(0, check('INPUT={}\n' + raw, '<whole62 statement contract>'))
        for value in ['source-full-PG3248', 'repository.MorningDatabaseSessionTest', 'repository/MorningDatabaseSession$Session', METHOD, "'mainRecompiled':False", "'vmActions':0", "'nativeImported':False"]:
            self.assertIn(value, raw)
        self.assertNotIn('platform.MorningBackupUnitCycleTest', raw)
        with self.assertRaises(ValueError): server('cycle')

    def test_literal27_rows_real_readonly_and_close_not_production_expected_helper(self):
        raw = Path(TEST).read_text(); start = raw.index('void ' + METHOD); end = raw.index('private static Optional<Throwable> mdb3254Fault', start)
        scope = raw[start:end]
        self.assertEqual(27, scope.count('{"'))
        self.assertIn('observer.executeQuery("SHOW transaction_read_only")', scope)
        self.assertIn('assertTrue(statement.isClosed())', scope)
        self.assertIn('assertSame(expected.orElseThrow(), actual)', scope)
        self.assertIn('mdb2292NoOwnerResources()', scope)
        self.assertNotIn('JdbcResourceFailures.replace(', scope)


if __name__ == '__main__':
    unittest.main()
