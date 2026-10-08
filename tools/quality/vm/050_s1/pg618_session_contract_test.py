"""Independent non-reset same-start dumps and foreign/out-of-window refusal; PT credit zero."""
import copy
import unittest
from pg618_collect_candidate_full import verify_sessions


def api():
    return [
        {'id': 'PUBLIC_A', 'start': '1001000', 'dump': '1002000'},
        {'id': 'PUBLIC_A', 'start': '1001000', 'dump': '1003000'},
        {'id': 'PUBLIC_B', 'start': '1004000', 'dump': '1005000'},
        {'id': 'PUBLIC_C', 'start': '1006000', 'dump': '1007000'},
        {'id': 'PUBLIC_D', 'start': '1000000', 'dump': '1010000'},
    ]


class SessionContract(unittest.TestCase):
    def test_same_start_strictly_later_dump_is_one_session_not_two_credits(self):
        self.assertEqual({'dumpRecords': 5, 'distinctSessions': 4},
                         verify_sessions(api(), 1000, 2000, 'api'))
        self.assertEqual({'dumpRecords': 1, 'distinctSessions': 1}, verify_sessions(
            [{'id': 'PUBLIC_ONE', 'start': '1000000', 'dump': '1001000'}],
            1000, 2000, 'protocol'))

    def test_bad_continuation_window_missing_unknown_null_and_topology(self):
        for field, value in [('start', '1001001'), ('dump', '1002000'),
                             ('dump', '1001999'), ('dump', '2001001'),
                             ('start', '998999'), ('start', '-1'), ('dump', None),
                             ('start', 1001000), ('id', None), ('id', '')]:
            rows = api(); rows[1][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                verify_sessions(rows, 1000, 2000, 'api')
        for rows in (None, [], {}, api()[:-1], api()+[copy.deepcopy(api()[0])]):
            with self.assertRaises(ValueError):
                verify_sessions(rows, 1000, 2000, 'api')
        for mode in ('foreign', 'missing', 'extra'):
            rows = api()
            if mode == 'foreign':
                rows[1]['id'] = 'FOREIGN_SESSION'
            elif mode == 'missing':
                del rows[1]['start']
            else:
                rows[1]['foreign'] = 'x'
            with self.assertRaises(ValueError):
                verify_sessions(rows, 1000, 2000, 'api')
        with self.assertRaises(ValueError):
            verify_sessions(api(), 1000, 2000, 'foreign')


if __name__ == '__main__':
    unittest.main()
