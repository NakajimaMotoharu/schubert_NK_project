"""Validate actual composed host code and sent STAGE schema, never execute transport."""
import ast
import json
import unittest
from pathlib import Path
import pg1349_current_bootstrap_dispatch as p

class Test(unittest.TestCase):
    def test_whole_current_stage_and_reservation(self):
        raw = p.source()
        tree = ast.parse(raw)
        stage = [n.value.value for n in ast.walk(tree) if isinstance(n, ast.Assign)
                 and any(isinstance(t, ast.Name) and t.id == 'payload' for t in n.targets)
                 and isinstance(n.value, ast.Constant) and isinstance(n.value.value, str)]
        self.assertEqual(1, len(stage))
        compile(stage[0], '<sent current immutable stage>', 'exec')
        self.assertIn('0.1.0-PG1292', stage[0])
        self.assertIn('cbca8738-3b24-4090-b77c-bf029677cdd6', stage[0])
        self.assertIn('pg1348-bootstrap-tools-v3', stage[0])
        for old in ('cc9ed874', 'PG932', 'pg983', 'pg963', '40ef6e894'):
            self.assertNotIn(old, raw)
        self.assertLess(raw.index("'.requested'"), raw.index("if action=='stage':"))
        self.assertLess(raw.index("pg1348-verify-v3.exit"), raw.index("'.requested'"))
        w = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
        full = json.loads((w / 'pg1340-published-terminal-post-v4.safe.json').read_bytes())
        frozen = json.loads((w / 'pg1348-frozen-v3.safe.json').read_bytes())
        self.assertEqual(full['productionSource'], frozen['productionSource'])
        self.assertTrue(full['genuineCompletion']['genuinePid1StartDone'])
        self.assertTrue(all('/' not in name for name in frozen['fileHashes']))

if __name__ == '__main__':
    unittest.main()
