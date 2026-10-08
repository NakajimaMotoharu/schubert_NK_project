"""Literal PID1/NKDONE1 vector and type/field/duplicate negative join matrix."""
import copy
import json
import unittest
from pg569_parent_join import completed_journal


class Test(unittest.TestCase):
    def setUp(self):
        self.rows = [{'_BOOT_ID': 'cc9ed8747f4f450ea1888de1e42c8441', '_PID': '1', '_UID': '0',
                      '_COMM': 'systemd', 'UNIT': 'schubert-nk-morning-controller.service',
                      'INVOCATION_ID': '075ad6644b284056a6cccf7af252519b',
                      '__MONOTONIC_TIMESTAMP': '46382089521', '__CURSOR': 'independent-one',
                      '__REALTIME_TIMESTAMP': '1791433679110604',
                      'MESSAGE_ID': '39f53479d3a045ac8e11786248231fbf', 'JOB_ID': '59402',
                      'JOB_TYPE': 'start', 'JOB_RESULT': 'done'}]
        self.rows.append(dict(self.rows[0], __CURSOR='independent-two',
                              MESSAGE_ID='7ad2d189f7e94e70a38c781354912448'))
        self.done = (b'NKDONE1\nb7e73994-b951-4696-bdd1-cfbc8a10e734\n2026-10-08T04:03:00.714124Z\n'
                     b'12f1af04-180e-405c-8738-853bbd875443\n2026-10-08T04:27:59.110604Z\n0\n')

    def raw(self, rows=None):
        return b''.join(json.dumps(row).encode() + b'\n' for row in (self.rows if rows is None else rows))

    def test_explicit_raw_to_typed_list_and_independent_monotonic_bound(self):
        rows, receipt = completed_journal(self.raw(), self.done)
        self.assertEqual(rows, self.rows)
        self.assertEqual(receipt['endMonotonicUs'], 46382089521)
        self.assertEqual(receipt['elapsedSeconds'], 1503.187759)
        self.assertTrue(receipt['genuineRootDone'])

    def test_bytes_list_null_duplicates_and_wrong_rows_deny(self):
        for raw in (None, self.rows, b'', self.raw()[:-1], b'null\n', b'[]\n', self.raw() + self.raw(),
                    b'{"_PID":"1","_PID":"2"}\n', b'\xff\n'):
            with self.assertRaises(ValueError): completed_journal(raw, self.done)
        for key, value in [('_PID', '2'), ('_UID', '1'), ('UNIT', 'wrong.service'),
                           ('INVOCATION_ID', None), ('__MONOTONIC_TIMESTAMP', True),
                           ('JOB_RESULT', 'failed'), ('JOB_ID', 'other')]:
            bad = copy.deepcopy(self.rows); bad[0][key] = value
            with self.assertRaises(ValueError): completed_journal(self.raw(bad), self.done)
        for done in (None, self.done[:-1], self.done.replace(b'\n0\n', b'\n1\n')):
            with self.assertRaises(ValueError): completed_journal(self.raw(), done)


if __name__ == '__main__':
    unittest.main()
