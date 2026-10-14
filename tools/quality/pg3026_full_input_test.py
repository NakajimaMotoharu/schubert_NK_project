"""Actual selected Test bytes + complete formatter-first all-module graph before dispatch."""
import subprocess
import unittest
from pyflakes.api import check
import pg3026_extra_row_full_six as full
import pg3028_extra_row_full_qualified as qualified


class WholeInputs(unittest.TestCase):
    def test_exact_selected_session61_and_failed_pair7(self):
        full.validate(subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip())

    def test_complete_format_before_pt_and_exact_counts(self):
        raw = full.server_source('a' * 40, 'b' * 64)
        self.assertEqual(0, check(raw, '<complete full3685 source>'))
        self.assertTrue(raw.index('format_result=subprocess.run') < raw.index("with(OUT/'maven.private.log')"))
        self.assertTrue('PG3026' in raw)
        q = qualified.server()
        self.assertTrue("'batch':(1285,173,568)" in q)
        self.assertFalse("'batch':(1284,173,568)" in q)


if __name__ == '__main__':
    unittest.main()
