"""Whole AST binding guard: literal oracle cannot overwrite sealed native globals."""
import ast
import json
import unittest
from pyflakes.api import check
from pg1446_current_cold_stage import W
import pg1257_fresh_independent_terminal_post as schema
import pg2980_scoped_resume_independent_post as post


class ScopedPost(unittest.TestCase):
    def test_complete_globals_and_local_oracle_exports(self):
        old = json.loads((W / 'pg2940-current-resume-before-v1/manifest.safe.json').read_bytes())
        raw = post.payload({n: old['proofHashes'][n]['sha256'] for n in schema.previous.SEALS})
        self.assertEqual(0, check('HASHES={}\nRECEIPT="fixture"\n' + raw, '<whole scoped post>'))
        tree = ast.parse(raw)
        fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'independent_resume_delta')
        self.assertFalse(any(isinstance(n, (ast.Global, ast.Nonlocal)) for n in ast.walk(fn)))
        ret = fn.body[-1]
        self.assertIsInstance(ret, ast.Return)
        self.assertEqual(['after', 'fresh_private', 'exec_record'], [n.id for n in ret.value.elts])
        roots = [n for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'root' for t in n.targets)]
        self.assertEqual(1, len(roots))
        self.assertIsInstance(roots[0].value, ast.BinOp)
        self.assertTrue("root = base / 'pg2890-native-stop-v1'" in raw)
        self.assertTrue("len(rows) == 24" in raw)
        self.assertTrue("preparedAfterSha256" in raw)
        self.assertTrue('from pg2970_configuration import same as config_same' in raw)


if __name__ == '__main__':
    unittest.main()
