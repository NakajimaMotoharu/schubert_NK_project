"""Actual whole current Main/helper/ABI/baseline/dispatch contracts, no VM writes."""
import ast
import unittest
import pg1396_existing_admin_sources as p
import pg1397_existing_admin_compile as c
import pg1398_existing_admin_dispatch as d

class Test(unittest.TestCase):
    def test_complete_current_source_and_baseline_join(self):
        golden='37715c53df9f698f1d544233eb8582595b0f90121e583228f8402b92c37f1ac0'
        v=p.files(golden);j='\n'.join(v.values())
        for s in ('Pg1396BootstrapExisting','PG998-bootstrap-guard',p.BEFORE,p.SOURCE,golden,'ordinary-bootstrap196','67108864','75132489604','400b2e34105149ff8f3a11c21da0be6a'):
            self.assertIn(s,j)
        for s in ('Pg1362BootstrapExisting','pg1344-current-bootstrap-before-v1','PG1396-bootstrap-guard'):
            # Rejection vector intentionally includes the four-digit wrong application.
            if s=='PG1396-bootstrap-guard':self.assertIn(s,v['Pg1396BootstrapDatabaseApplicationTest.java'])
            else:self.assertNotIn(s,j)
        for name,raw in v.items():
            if name.endswith('.py'):ast.parse(raw)
        self.assertIn("if action=='execute':assert(W/'pg1396-verify-v3.exit')",d.source())
        self.assertIn('existingRoleVerificationNormalClose',d.source())
        self.assertIn("pg1387-prepare-v1.exit",d.source())
        self.assertIn('Pg1396BootstrapDatabaseApplicationTest',c.source())
        self.assertIn('pg1396_existing_admin_sources_test.py',c.source())
        self.assertIn(p.BEFORE,c.source())

if __name__=='__main__':unittest.main()
