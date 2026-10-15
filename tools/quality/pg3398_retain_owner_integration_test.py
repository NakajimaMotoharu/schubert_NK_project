import ast
import unittest

import pg3398_retain_owner_integration as current


class IntegrationTemplates(unittest.TestCase):
    def test_actual_digest_fragments_are_never_changed(self):
        head = '3706' + 'a' * 36; digest = '3706' + 'b' * 60
        raw = current.server_source(head, digest)
        values = [n.value for n in ast.walk(ast.parse(raw)) if isinstance(n, ast.Constant)]
        self.assertIn(head, values); self.assertIn(digest, values)
        self.assertNotIn('f0' * 20, values); self.assertNotIn('e1' * 32, values)
        self.assertIn(3707, values); self.assertIn(543, values)

    def test_independent_counts_and_historical_data_are_separate(self):
        raw = current.independent_server(); tree = ast.parse(raw)
        tuples = [ast.literal_eval(n) for n in ast.walk(tree) if isinstance(n, ast.Tuple)
                  and all(isinstance(v, ast.Constant) for v in n.elts)]
        self.assertIn((1303, 174, 568), tuples)
        self.assertNotIn((1302, 173, 568), tuples)
        compile(raw, '<fixed independent3707>', 'exec')


if __name__ == '__main__':
    unittest.main()
