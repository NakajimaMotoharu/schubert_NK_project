import unittest
from pyflakes.api import check
from pg2650_operation_post_full_six import server_source, ALLOWED, validate
import subprocess


class NewCandidateFull(unittest.TestCase):
    def test_exact_candidate_counts_and_namespace(self):
        raw=server_source('1'*40,'2'*64)
        self.assertEqual(0,check(raw,'<candidate whole full>'))
        for marker in ['PG2650','3666','541','1643']:self.assertIn(marker,raw)
        self.assertNotIn('PG2640',raw)
        self.assertEqual(9,len(ALLOWED))

    def test_current_whole_selected_inputs(self):
        validate(subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip())


if __name__=='__main__':unittest.main()
