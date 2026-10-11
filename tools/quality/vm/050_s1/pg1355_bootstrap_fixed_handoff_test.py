"""Actual qualified public owner schema and generated metadata conversion."""
import ast
import json
from pathlib import Path
import unittest
import pg1355_bootstrap_fixed_handoff_v2 as p

class Test(unittest.TestCase):
    def test_exact_nine_values_roundtrip(self):
        raw = p.payload(dict.fromkeys(p.previous.prior.previous.prior.prior.previous.transport.previous.SEALS, 'b' * 64))
        tree = ast.parse(raw)
        node = next(n for n in ast.walk(tree) if isinstance(n, ast.Assign)
                    and isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Name)
                    and n.value.func.id == 'list' and 'metadata9(st)' in ast.unparse(n))
        expression = compile(ast.Expression(body=node.value), '<sent owner metadata>', 'eval')
        public = json.loads(Path('/home/mini/codex/project1/work/pgpt-runs/PG379/pg1352-bootstrap-expired-peer-v1.safe.json').read_bytes())['fixedOwner']
        for values in public['locks'].values():
            self.assertEqual(9, len(values))
            actual = eval(expression, {'metadata9': lambda ignored: tuple(values), 'st':None})
            self.assertEqual(values, actual)
            self.assertEqual(actual, json.loads(json.dumps(actual)))
            for index in range(9):
                changed = list(actual);changed[index] += 1
                self.assertNotEqual(values, changed)
        self.assertIn(p.previous.PROOF, raw)
        self.assertIn('terminate_once(838452,7697543', raw)
        self.assertNotIn('pg1353-bootstrap-fixed-handoff-v1', raw)

if __name__ == '__main__':
    unittest.main()
