"""Literal new API child session topology and changed-candidate reference policy."""
import unittest
from pg714_full_collect import source

env = {'__name__': 'inert_whole_policy'}
exec(compile(source(), '<pure qualification policy>', 'exec'), env)


class Test(unittest.TestCase):
    def rows(self):
        return [{'id': 'PUBLIC-' + str(i), 'start': str(1000000+i), 'dump': '1005000'} for i in range(6)] + [{'id': 'PUBLIC-0', 'start': '1000000', 'dump': '1006000'}]

    def test_actual_external_two_more_sessions_and_strict_continuations(self):
        check = env['verify_sessions']
        self.assertEqual(check(self.rows(), 1000, 1010, 'api'), {'dumpRecords': 7, 'distinctSessions': 6})
        for key, bad in ({'id': 'PUBLIC-FOREIGN', 'start': '1000001', 'dump': '1005000'}).items():
            rows = self.rows(); rows[-1][key] = bad
            with self.subTest(key=key), self.assertRaises(ValueError): check(rows, 1000, 1010, 'api')
        for bad in (None, [], self.rows()[:-2]):
            with self.assertRaises(ValueError): check(bad, 1000, 1010, 'api')
        for bad in (True, '9999999', 'unknown'):
            rows = self.rows(); rows[-1]['dump'] = bad
            with self.assertRaises(ValueError): check(rows, 1000, 1010, 'api')
        rows = self.rows(); rows[-1]['extra'] = 'unknown'
        with self.assertRaises(ValueError): check(rows, 1000, 1010, 'api')

    def test_only_fresh_qualified_candidate_and_six_no_skip_gates(self):
        raw = source()
        for literal in ('3502, 283, None', 'suites == 517 and total_classes == 1614',
                        'pg713-expiry-six-host-v1', 'pg712-expiry-core-qualification-v1',
                        'pg711-expiry-core-v1/batch', "bugs.findall('.//Error')", "'api': (7, 6)"):
            self.assertIn(literal, raw)
        self.assertNotIn('pg630-retention-factory-six-host-v1', raw)


if __name__ == '__main__': unittest.main()
