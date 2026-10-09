"""Independent AST checks actual SQL count and receipt, no operation authority."""
import ast
import unittest
from pg719_post_v2 import source


class CountTest(unittest.TestCase):
    def test_actual_and_reported_count_and_new_slot(self):
        raw = source()
        tree = ast.parse(raw)
        payload = next(ast.literal_eval(n.value) for n in tree.body
                       if isinstance(n, ast.Assign) and any(
                           isinstance(t, ast.Name) and t.id == 'PAYLOAD' for t in n.targets))
        ast.parse(payload)
        self.assertIn("len(after['rows']['schubert.batch_runs'])==524", payload)
        dictionaries = [n for n in ast.walk(ast.parse(payload)) if isinstance(n, ast.Dict)]
        counts = [ast.literal_eval(v) for d in dictionaries for k, v in zip(d.keys, d.values)
                  if isinstance(k, ast.Constant) and k.value == 'batchRows']
        self.assertEqual([524], counts)
        self.assertIn("'pg719-'+mode+'-post-v2'", raw)
        for mutation in ('systemctl start', 'systemctl stop', 'os.replace(', 'os.unlink('):
            self.assertNotIn(mutation, payload)


if __name__ == '__main__':
    unittest.main()
