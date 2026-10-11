"""Whole actual helper/main DB label contract, not just namespace strings."""
import ast
import unittest
import pg1356_current_bootstrap_sources as p
import pg1357_current_bootstrap_compile as c

class Test(unittest.TestCase):
    def test_fixed_db_application_shared_by_actual_ports(self):
        values = p.files('b'*64)
        joined = '\n'.join(raw for name, raw in values.items() if name != 'Pg1356BootstrapDatabaseApplicationTest.java')
        self.assertFalse('PG1356-bootstrap-guard' in joined)
        for name in ('Pg1356BootstrapExisting.java', 'pg1356_bootstrap_existing.py', 'pg1356_db_contract.py'):
            self.assertIn('PG998-bootstrap-guard', values[name])
        self.assertIn('PG1356-bootstrap-guard', values['Pg1356BootstrapDatabaseApplicationTest.java'])
        for name, raw in values.items():
            if name.endswith('.py'):
                ast.parse(raw)
        self.assertIn('db-application-oracle', c.source())
        self.assertIn("str(target/'Pg1356BootstrapDatabaseApplicationTest.java')", c.source())
        self.assertIn('pg1356-frozen-v3.safe.json', c.source())

if __name__ == '__main__':
    unittest.main()
