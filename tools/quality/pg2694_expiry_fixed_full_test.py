import unittest
from pyflakes.api import check
from pg2694_expiry_fixed_full_six import server_source
from pg2695_expiry_fixed_full_qualified import server


class FreshFixedFull(unittest.TestCase):
    def test_new_namespace_complete_counts_and_no_old_qualification(self):
        for raw in [server_source('a'*40,'b'*64),server()]:
            self.assertEqual(0,check(raw,'<whole fixed full namespace>'))
            compile(raw,'<whole fixed full namespace>','exec')
            self.assertNotIn('PG2650',raw)
            for marker in ['PG2694','3666','541','1643']:self.assertIn(marker,raw)


if __name__=='__main__':unittest.main()
