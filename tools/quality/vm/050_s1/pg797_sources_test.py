import ast
import unittest
from pathlib import Path
from pg797_sources import java,helper


class Test(unittest.TestCase):
    def test_current_source_and_no_mutation_surface(self):
        raw=java();data=helper();ast.parse(data)
        for literal in ('PG797-fixed-recovery','PG797-fixed-snapshot','batchLease.verify();schemaLease.verify();','Thread.sleep(5000)','toNanos(75)','batchLease.confirmClosed();schemaLease.confirmClosed();','PG797_DB_NOT_CONFIRMED','pg797-liveness-tools-v1','pg797_owned.py','actualNames().equals(retiredNames())'):
            self.assertIn(literal,raw)
        for forbidden in ('files.revoke(','RootFailedStartRecovery.retirePair(','helper("stop:','pg783_','pg779_'):self.assertNotIn(forbidden,raw)
        self.assertIn('pg787-retired-post-v1/after.private.json',data)
        self.assertIn("action in ('verify','capture')",data)
        # Actual assembly includes both private helper entry points and three Java source files.
        compile_source=(Path(__file__).parent/'pg797_compile.py').read_text();ast.parse(compile_source)
        self.assertIn('Pg797OwnedDatabaseTest.java',compile_source)


if __name__=='__main__':unittest.main()
