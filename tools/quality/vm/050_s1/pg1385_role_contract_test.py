"""Actual whole Java/helper/compiler dependency contract and SQL negative fixture."""
import ast
import unittest
import pg1380_bootstrap_role_sources_v3 as source
import pg1385_role_compile_v3 as compiler
from pg1380_bootstrap_role_sql_test import Test as SqlTest

class Contract(unittest.TestCase):
    def test_whole_generated_dependency_join(self):
        values=source.files();joined='\n'.join(values.values());raw=compiler.text()
        self.assertIn('import dev.codex.schubert.nk.batch.repository.*;',values['Pg1380BootstrapRolePreparation.java'])
        self.assertIn('Pg1380BootstrapRolePreparation',joined)
        self.assertIn('pg1380-bootstrap-role-tools-v2',joined)
        self.assertIn('pg1380-bootstrap-role-prepare-v1',joined)
        self.assertIn('PG998-bootstrap-role',joined)
        self.assertIn('pg1385-frozen-v2.safe.json',raw)
        self.assertIn('pg1382-role-fixed-ref-handoff-v1',raw)
        self.assertIn('pg1383-role-sql-parse-v1',raw)
        self.assertIn("(R/'Pg1372BootstrapRoleArgumentTest.java')",raw)
        self.assertIn("replace('Pg1372','Pg1380')",raw)
        for old in ('Pg1374BootstrapRolePreparation','pg1374-bootstrap-role','PG1380-bootstrap-role'):
            self.assertNotIn(old,joined)
        ast.parse(values['pg1380_bootstrap_role_refs.py'])

if __name__=='__main__':unittest.main()
