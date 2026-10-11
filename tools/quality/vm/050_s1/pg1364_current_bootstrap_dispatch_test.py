"""Actual new namespace/runtime recovery/compiler/before complete join."""
import ast
import json
from pathlib import Path
import unittest
import pg1364_current_bootstrap_dispatch as p

class Test(unittest.TestCase):
    def test_actual_sent_payload(self):
        raw=p.source();tree=ast.parse(raw)
        stage=next(n.value.value for n in ast.walk(tree)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='payload'for t in n.targets)and isinstance(n.value,ast.Constant)and isinstance(n.value.value,str))
        compile(stage,'<actual stage>','exec')
        self.assertTrue('pg1362-bootstrap-tools-v3'in stage and 'PG1292'in stage)
        self.assertTrue('pg1362-frozen-v3.safe.json'in raw)
        self.assertTrue('pg1361-bootstrap-fixed-pair-handoff-v1.exit'in raw)
        self.assertTrue('pg1356-verify-v3.exit'in raw)
        self.assertTrue(raw.index("'.requested'")<raw.index("if action=='stage':"))
        w=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
        frozen=json.loads((w/'pg1362-frozen-v3.safe.json').read_bytes())
        self.assertEqual('769ddb15cd735c25fef581b5f9850ef9d0053c0f',frozen['productionSource'])
        self.assertEqual(b'0\n',(w/'pg1362-db-application-oracle-v3.exit').read_bytes())
        self.assertTrue(all('/'not in name for name in frozen['fileHashes']))

if __name__=='__main__':
    unittest.main()
