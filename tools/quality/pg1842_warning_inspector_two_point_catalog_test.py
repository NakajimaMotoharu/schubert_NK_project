"""Two native dumps can differ; no same-byte or fabricated second execution."""
import ast
import unittest
from pg1842_warning_inspector_two_point_catalog import catalog_source


class Points(unittest.TestCase):
    def test_both_points_independent_bytes_full_archive_and_no_old_same_byte_guard(self):
        raw=catalog_source('def completed(rows,original): return {}\n');compile(raw,'<actual points>','exec')
        self.assertIn('len(selected)==10',raw)
        self.assertIn("names.extend([(closing,'schubert-nk-inbox-inspector.service'),(earlier,'schubert-nk-inbox-inspector.service')])",raw)
        self.assertNotIn('early_bytes',raw);self.assertNotIn('relative==earlier',raw)
        self.assertIn('set(excluded)==set(old)-',raw)
        tree=ast.parse(raw);calls=[ast.unparse(n)for n in ast.walk(tree)if isinstance(n,ast.Call)]
        self.assertTrue(any('hashlib.sha256(raw)'in c for c in calls))


if __name__=='__main__':unittest.main()
