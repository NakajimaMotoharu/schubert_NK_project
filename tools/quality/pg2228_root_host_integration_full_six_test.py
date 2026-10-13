import unittest
from pg2228_root_host_integration_full_six import server_source
from pyflakes.api import check


class FullScope(unittest.TestCase):
    def test_actual_whole_six_fixed_scope_not_management_only(self):
        s=server_source('a'*40,'b'*64)
        self.assertEqual(0,check(s,'<actual current full3633>'))
        for value in ['PG2228','3633','540','1643','3b7f3567b54f91f3a9dbeb859e8dd77e8353a2c8']:
            self.assertIn(value,s)
        self.assertNotIn('PG2124-six-v1',s)
        self.assertNotIn('-DskipTests',s)


if __name__=='__main__':unittest.main()
