import unittest
from pyflakes.api import check
from pg2651_operation_post_full_qualified import server


class NewCandidateFullQualification(unittest.TestCase):
    def test_full_source_counts_and_scope(self):
        raw=server();self.assertEqual(0,check(raw,'<whole candidate qualifier>'))
        for marker in ['PG2650','3666','541','1643',"'web':(888,130,315)"]:
            self.assertIn(marker,raw)
        self.assertNotIn('PG2640',raw)


if __name__=='__main__':unittest.main()
