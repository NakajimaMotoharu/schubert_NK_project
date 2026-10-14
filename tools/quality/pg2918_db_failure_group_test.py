"""Actual selected hash/role qualification and complete full count basis before dispatch."""
import subprocess
import unittest
from pyflakes.api import check
import pg2918_db_failure_group_full_six as p


class FullInputQualification(unittest.TestCase):
    def test_actual_selected_whole_inputs_are_preserved(self):
        p.validate(subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip())

    def test_full_server_whole_namespace_and_count(self):
        raw=p.server_source('a'*40,'b'*64)
        self.assertEqual(0,check(raw,'<whole3684 server>'))
        for s in ['PG2918','3684','542','1643',p.SOURCE]:self.assertIn(s,raw)
        self.assertNotIn('PG2798',raw)


if __name__=='__main__':unittest.main()
