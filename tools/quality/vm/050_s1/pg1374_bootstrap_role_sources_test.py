"""Actual whole new files/main/host namespace join, no guest actions."""
import ast
import unittest
import pg1374_bootstrap_role_sources_v2 as p
import pg1375_bootstrap_role_compile_v2 as c

class Test(unittest.TestCase):
    def test_actual_imports_tuple_and_generated_files(self):
        values=p.files();joined='\n'.join(values.values())
        self.assertTrue('import dev.codex.schubert.nk.batch.repository.*;'in values['Pg1374BootstrapRolePreparation.java'])
        self.assertTrue('Pg1374BootstrapRolePreparation'in joined)
        self.assertFalse('Pg1372BootstrapRolePreparation'in joined)
        self.assertTrue('pg1374-bootstrap-role-tools-v2'in joined)
        self.assertFalse('pg1374-bootstrap-role-tools-v1'in joined)
        self.assertTrue('PG998-bootstrap-role'in joined)
        ast.parse(values['pg1374_bootstrap_role_refs.py'])
        self.assertTrue('pg1374-bootstrap-role-tools-v2'in c.text())
        self.assertTrue('pg1375-frozen-v2.safe.json'in c.text())

if __name__=='__main__':unittest.main()
