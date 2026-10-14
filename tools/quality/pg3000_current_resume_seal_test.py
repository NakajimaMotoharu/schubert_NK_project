"""Independent whole-input shape/negative guard/native lineage and scope exports."""
import ast
import json
import unittest
from pg1446_current_cold_stage import W
import pg3000_current_resume_full_seal as seal


class WholeSeal(unittest.TestCase):
    def test_complete_current_source_and_no_raw_before_rewrite(self):
        v = json.loads((W / 'pg2990-current-resume-live-binding-v1/manifest.safe.json').read_bytes())
        raw = seal.payload({**v['binding'], 'rootPid': v['rootPid']})
        tree = ast.parse(raw)
        for token in ['d10735e678e5053c0c96c55a42f65f2302132cfae902edd81dffbc2275c4c4ac', 'c1170b22495c28a114640f2f1153c92c9fa673431b0fc35e4e0039d0ca9cb510', '96757f38127024e527c5356308e1d6337fb1bb50b2e258283bf2d2fc00376423', 'len(manifest)==10', 'pg2984-current-fresh-resume-once-v1', '0.1.0-PG2802', '79a3260a-e16d-42bf-942a-b914ed144c28']:
            self.assertTrue(token in raw, token)
        self.assertFalse('pg2356-current-runtime-verification-post-v1' in raw)
        constants = {t.id: n.value.value for n in tree.body if isinstance(n, ast.Assign) and isinstance(n.value, ast.Constant) for t in n.targets if isinstance(t, ast.Name) and t.id in ['GUARD', 'ORACLE']}
        comparisons = [n for n in ast.walk(ast.parse(constants['GUARD'])) if isinstance(n, ast.Compare) and isinstance(n.left, ast.Call) and isinstance(n.left.func, ast.Attribute) and isinstance(n.left.func.value, ast.Name) and n.left.func.value.id == 'binding' and n.left.func.attr == 'get' and n.left.args and isinstance(n.left.args[0], ast.Constant) and n.left.args[0].value == 'run']
        equality_literals = [v.value for n in comparisons if any(isinstance(op, ast.Eq) for op in n.ops) for v in n.comparators if isinstance(v, ast.Constant)]
        self.assertIn('91f5484b-9702-4c7c-97f3-dd5110a853f9', equality_literals)
        self.assertNotIn('0dc63b79-3f9a-450c-b2a6-56f86272d272', equality_literals)
        self.assertTrue('2026-10-14T23:00:40.252177+00:00' in constants['ORACLE'])
        fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'native_before_anchor')
        self.assertFalse(any(isinstance(n, (ast.Global, ast.Nonlocal)) for n in ast.walk(fn)))
        self.assertIsInstance(fn.body[-1], ast.Return)


if __name__ == '__main__':
    unittest.main()
