import unittest
from pyflakes.api import check
from pg2300_jdbc_host_integration_full_six import server_source,validate
from pg2301_jdbc_host_integration_qualified import server


class FullIntegration(unittest.TestCase):
    def test_whole_source_scope_and_independent_qualifier(self):
        run=server_source('a'*40,'b'*64)
        proof=server()
        for raw in [run,proof]:
            self.assertEqual(0,check(raw,'<actual full JDBC source>'))
            for literal in ['PG2300','3635','540','1643']:
                self.assertIn(literal,raw)
            self.assertNotIn('PG2228-six-v1',raw)
            self.assertNotIn('-DskipTests',raw)
        self.assertIn("'batch':(1238,172,568)",proof)

    def test_selected_provenance_current_and_foreign(self):
        validate('d7d75940ae740ce88e0cc7e62ca58a07280f8d81')
        with self.assertRaises(ValueError):
            validate('3b7f3567b54f91f3a9dbeb859e8dd77e8353a2c8')


if __name__=='__main__':unittest.main()
