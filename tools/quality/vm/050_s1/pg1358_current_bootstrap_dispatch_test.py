"""Actual sent schema + before/recovery/compile join; no transport mutation."""
import ast
import json
from pathlib import Path
import unittest
import pg1358_current_bootstrap_dispatch as p

class Test(unittest.TestCase):
    def test_sent_and_host_schema_current_complete(self):
        raw = p.source()
        tree = ast.parse(raw)
        stage = next(n.value.value for n in ast.walk(tree) if isinstance(n, ast.Assign)
                     and any(isinstance(t,ast.Name) and t.id=='payload' for t in n.targets)
                     and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str))
        compile(stage, '<actual stage>', 'exec')
        for required in ('PG1292', 'cbca8738-3b24-4090-b77c-bf029677cdd6', 'pg1356-bootstrap-tools-v3'):
            self.assertTrue(required in stage)
        self.assertTrue("pg1356-verify-v3.exit" in raw)
        self.assertTrue("pg1355-bootstrap-fixed-handoff-v2.exit" in raw)
        self.assertTrue("pg1348-verify-v3.exit" in raw)
        self.assertTrue(raw.index("'.requested'") < raw.index("if action=='stage':"))
        w = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
        frozen = json.loads((w/'pg1356-frozen-v3.safe.json').read_bytes())
        self.assertEqual('769ddb15cd735c25fef581b5f9850ef9d0053c0f', frozen['productionSource'])
        self.assertEqual('f64ed4689d2c52e2227f771f7870414686ff0e6f52a6dc7b3d1b22313668428d', frozen['beforeSha256'])
        self.assertTrue('Pg1356BootstrapDatabaseApplicationTest.class' in frozen['fileHashes'])
        self.assertEqual(b'0\n', (w/'pg1356-db-application-oracle-v3.exit').read_bytes())
        self.assertTrue(all('/' not in name for name in frozen['fileHashes']))

if __name__ == '__main__':
    unittest.main()
