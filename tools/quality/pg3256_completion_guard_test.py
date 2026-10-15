"""Exact current Main and two actually selected Test method membership."""
import unittest
from pyflakes.api import check
from pg3256_completion_guard_selected import server, METHODS


class CompletionGuard(unittest.TestCase):
    def test_whole_namespace_and_two_case_names(self):
        raw = server('statement')
        self.assertEqual(0, check('INPUT={}\n' + raw, '<all63 fixed Session>'))
        for value in METHODS + ['source-full-PG3248', 'repository.MorningDatabaseSessionTest', 'repository/MorningDatabaseSession$Session', "'mainRecompiled':False", "'vmActions':0"]:
            self.assertIn(value, raw)
        self.assertNotIn('PG3254', raw)


if __name__ == '__main__':
    unittest.main()
