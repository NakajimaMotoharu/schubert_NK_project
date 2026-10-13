import unittest
from pyflakes.api import check
from pg2404_question_jdbc_full_six import server_source, validate, production
from pg2405_question_jdbc_full_qualified import server


class Full(unittest.TestCase):
    def test_all_modules_fixed_counts_new_source_and_no_skip(self):
        for raw in [server_source('a'*40, 'b'*64), server()]:
            self.assertEqual(0, check(raw, '<new current full>'))
            for value in ['PG2404', '3637', '540', '1643', production()]:
                self.assertIn(value, raw)
            self.assertNotIn('-DskipTests', raw)
        self.assertIn("'batch':(1240,172,568)", server())

    def test_only_minimal_approved_resource_and_passed_jdbc_delta(self):
        validate(production())
        with self.assertRaises(ValueError):
            validate('729c19b2f3b6e65168224498baaa140629cd0695')


if __name__ == '__main__':
    unittest.main()
