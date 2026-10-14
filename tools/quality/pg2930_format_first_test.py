"""Actual whole assembled server refuses any module format failure before test execution."""
import unittest
from pyflakes.api import check
import pg2926_jdbc_format_selected as selected
import pg2930_format_fixed_db_full_six as full


class FormatFirst(unittest.TestCase):
    def test_exact_named_input_and_whole_first_format_gate(self):
        self.assertIn('ROOT/TEST',selected.transport_body())
        self.assertIn('PG2926-candidate-v1',selected.server())
        raw=full.server_source('a'*40,'b'*64)
        self.assertEqual(0,check(raw,'<whole six-module format first>'))
        self.assertLess(raw.index('format_result=subprocess.run'),raw.index("with(OUT/'maven.private.log')"))
        self.assertIn("format_result.returncode!=0",raw)
        for v in ['PG2930','3684','542','1643']:self.assertIn(v,raw)


if __name__=='__main__':unittest.main()
