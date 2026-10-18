"""All independent post functions preserved; enriched data inside held tenRef only."""
import ast
import unittest
from pyflakes.api import check, checkPath
import pg5080_current_bootstrap_before as target


class CurrentBefore(unittest.TestCase):
    def test_current_all_original_functions_unchanged(self):
        raw = target.payload()
        old = (target.admission.W / target.post.SLOT / 'payload.private.py').read_text()
        functions = lambda text: {n.name: ast.dump(n, include_attributes=False)
                                  for n in ast.parse(text).body if isinstance(n, ast.FunctionDef)}
        original, current = functions(old), functions(raw)
        self.assertTrue(set(original) <= set(current))
        for name, body in original.items():
            self.assertEqual(body, current[name], name)
        for literal in (target.SOURCE, target.BOM, target.AFTER, target.SLOT):
            self.assertIn(literal, raw)
        for forbidden in ('StartUnit', 'StopUnit', 'reset-failed', 'daemon-reload',
                          "save=base/'pg5066-current-owned-post-v1'"):
            self.assertNotIn(forbidden, raw)
        self.assertEqual(0, check(raw, '<current stopped enriched whole>'))

    def test_enrichment_is_readonly_and_refs_finally_returned(self):
        tree = ast.parse(target.payload())
        scope = next(n for n in tree.body if isinstance(n, ast.Try) and n.finalbody)
        body = ast.unparse(ast.Module(body=scope.body, type_ignores=[]))
        final = ast.unparse(ast.Module(body=scope.finalbody, type_ignores=[]))
        for literal in ("users[0]['role'] == 'ADMIN'", 'bootstrap-admin-username',
                        'bootstrap-admin-password', 'dependency_graph', "'native': native", 'os.fsync'):
            self.assertIn(literal, body)
        self.assertIn('UnrefUnit', final)
        self.assertIn('bus.close()', final)
        for path in (target.__file__, __file__):
            self.assertEqual(0, checkPath(path))


if __name__ == '__main__':
    unittest.main()
